import openai
from config.config import OPENAI_MODEL

def generate_explanation(test_name, value, unit, normal_range):
    prompt = (
        f"The lab test result shows that the {test_name} is {value} {unit}, "
        f"while the normal range is {normal_range}. Explain in simple terms what this means, "
        "and if it is low or high, suggest possible causes or next steps."
    )
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": "You are a helpful medical assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        explanation = response["choices"][0]["message"]["content"]
        return explanation
    except Exception as e:
        return f"Error generating explanation: {e}"

def generate_summary_and_suggestions(structured_data):
    abnormal_tests = [row for _, row in structured_data.iterrows() if row['Flag'] != "Normal"]

    if not abnormal_tests:
        return "All test results appear normal. No immediate concerns.", []

    summary_prompt = (
        "Here are some abnormal lab results:\n\n"
        + "\n".join([f"{t['Test']}: {t['Value']} {t['Unit']} (Normal: {t['Normal Range']})"
                    for t in abnormal_tests]) + "\n\n"
        "Generate a brief health summary and suggest what actions or specialists the patient should consider."
    )

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": "You are a medical assistant that gives helpful follow-up advice."},
                      {"role": "user", "content": summary_prompt}],
            temperature=0.7,
            max_tokens=200
        )
        summary_text = response['choices'][0]['message']['content']
        return summary_text, abnormal_tests
    except Exception as e:
        return f"Error generating summary: {e}", []
