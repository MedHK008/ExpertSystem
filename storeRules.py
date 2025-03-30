from pymongo import MongoClient
import re

def parse_condition(condition_str):
    condition_str = condition_str.strip()
    
    if condition_str.startswith('(') and condition_str.endswith(')'):
        return parse_condition(condition_str[1:-1].strip())
    
    def split_by_operator(s, operator):
        parts = []
        current = []
        depth = 0
        op_len = len(operator)
        i = 0
        while i < len(s):
            if s[i] == '(':
                depth += 1
                current.append(s[i])
                i += 1
            elif s[i] == ')':
                depth -= 1
                current.append(s[i])
                i += 1
            elif depth == 0 and s[i:i+op_len].upper() == operator.upper():
                parts.append(''.join(current).strip())
                current = []
                i += op_len
                while i < len(s) and s[i] == ' ':  # Skip spaces after operator
                    i += 1
            else:
                current.append(s[i])
                i += 1
        parts.append(''.join(current).strip())
        return parts

    # Try AND first
    and_parts = split_by_operator(condition_str, 'ET')
    if len(and_parts) > 1:
        return {
            "operator": "AND",
            "items": [parse_condition(p) for p in and_parts]
        }
    
    # Then try OR
    or_parts = split_by_operator(condition_str, 'OU')
    if len(or_parts) > 1:
        return {
            "operator": "OR",
            "items": [parse_condition(p) for p in or_parts]
        }
    
    # Base case: simple condition
    var_value = re.split(r'\s*=\s*', condition_str, 1)
    return {"variable": var_value[0].strip(), "value": var_value[1].strip()}


def parse_rule(rule_text, rule_number):
    try:
        # Split SI and ALORS parts
        if 'ALORS' not in rule_text:
            raise ValueError("Missing 'ALORS' in rule text")
        si_part, alors_part = re.split(r'\s*ALORS\s*', rule_text, 1, flags=re.IGNORECASE)
        
        # Clean SI condition
        si_condition = re.sub(r'^SI\s*', '', si_part, flags=re.IGNORECASE).strip()
        si_condition = re.split(r'\s*\(.*?\)\s*$', si_condition)[0]  # Remove trailing comments
        
        # Clean ALORS conclusion
        alors_conclusion = alors_part.split('(')[0].strip()
        risk_match = re.search(r'Risque\s*=\s*(\w+)', alors_conclusion, re.IGNORECASE)
        if not risk_match:
            raise ValueError("Risk level not found in conclusion")
        risk_level = risk_match.group(1).capitalize()
        
        return {
            "rule_number": rule_number,
            "conditions": parse_condition(si_condition),
            "conclusion": {"Risque": risk_level}
        }
    except Exception as e:
        raise ValueError(f"Error parsing rule: {str(e)}")

def load_rules_to_mongodb(file_path):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["geofencingDB"]
    rules_collection = db["rules"]
    rules_collection.delete_many({})
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    rule_pattern = r'Règle\s+(\d+)\s*:\s*\n([\s\S]*?)(?=\n\s*Règle\s+\d+|$)'
    raw_rules = re.findall(rule_pattern, content, re.IGNORECASE)
    
    for rule_number, rule_body in raw_rules:
        try:
            rule_number = int(rule_number)
            rule_data = parse_rule(rule_body.strip(), rule_number)
            rules_collection.insert_one(rule_data)
            print(f"Inserted Rule {rule_number}")
        except Exception as e:
            print(f"Error processing Rule {rule_number}: {str(e)}")
            continue

if __name__ == "__main__":
    load_rules_to_mongodb("regles.txt")
    print("Rules loaded successfully!")