import re

def parse_lab_results(text):
    lines = text.split("\n")
    results = []

    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue
        
        parts = re.split(r'\s{2,}', line)
        if len(parts) < 2:
            tokens = line.split()
            num_idx = -1
            for i, t in enumerate(tokens):
                try:
                    float(t)
                    num_idx = i
                    break
                except:
                    continue
            if num_idx == -1 or num_idx == 0:
                continue
            test_name = " ".join(tokens[:num_idx])
            value = tokens[num_idx]
            unit = tokens[num_idx+1] if len(tokens) > num_idx+1 else ""
            normal_range = ""
        else:
            test_name = parts[0]
            rest = parts[1].split()
            if len(rest) == 0:
                continue
            value = rest[0]
            unit = rest[1] if len(rest) > 1 else ""
            normal_range = " ".join(rest[2:]) if len(rest) > 2 else ""

        try:
            value_float = float(value)
        except:
            continue

        flag = "Normal"
        if "-" in normal_range:
            try:
                low, high = normal_range.split("-")
                low = float(low.strip())
                high = float(high.strip())
                if value_float < low:
                    flag = "Low"
                elif value_float > high:
                    flag = "High"
            except:
                pass
        
        results.append({
            "Test": test_name.strip(),
            "Value": value_float,
            "Unit": unit,
            "Normal Range": normal_range.strip(),
            "Flag": flag
        })

    return results
