from pathlib import Path
from ollama import chat
import json



question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## WRITE ##
service_status = {
    "wifi": "operational"
}

state = {
    "problem": question,
    "wi_fi status": "operational",
    "wi-fi_check": True
}

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )

with open("state.json", "r") as file:
    state = json.load(file)

print(state)


## SELECT CONTEXT FILES BASED ON QUESTION
## Create the function that takes the student's question, takes some keywords and chooses the relevant files from the knowledge base. Return a list of the selected files.
## For example, if the question has the kyeword "print" or "printer", then the function should return the file "knowledge/printer_setup.txt" in a list.
def select_context(question):
    text = question_text.lower()
    selected_files = []

    if "wi-fi" in text or "wifi" in text or "network" in text or "connect" in text:
        selected_files.append("knowledge/wifi_setup.txt")

    if "password" in text or "credential" in text:
        selected_files.append("knowledge/password_changes.txt")

    if "print" in text or "printer" in text:
        selected_files.append("knowledge/printing.txt")

    if "email" in text:
        selected_files.append("knowledge/email_setup.txt")

    if "vpn" in text:
        selected_files.append("knowledge/vpn.txt")

    if "projector" in text or "display" in text:
        selected_files.append("knowledge/classroom_projectors.txt")

    if "status" in text or "outage" in text:
        selected_files.append("knowledge/service_status.txt")

    return selected_files


selected_files = select_context(question)
print("Selected files:", selected_files)

## READ SELECTED FILES and add their contents to the context variable.
context = ""


## 
## COMPRESS CONTEXT
## Add logic to compress the context from above by calling Qwen with "context" and the "question" as the parameter
## The response from Qwen should be the compressed context. Store it in a variable called "compressed_context" 

def compress_context(context, question):
    prompt = f"""
You are a university IT support assistant.
Compress the context below.
Keep only the information that is relevant to the student's question.
Remove unrelated setup details.

Student question:
{question}

Context:
{context}
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": "You compress technical support context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content


compressed_context = compress_context(context, question)





## Print the length of the compressed context
print("Context characters:", len(context))
print("Compressed context characters:", len(compressed_context))

## Now, call Qwen again with the compressed context and the student's question. Store the response in a variable called "response" and print the response from Qwen.
## Ensure the model produces a structured output 
def parse_json_response(response_text):
    text = response_text.strip()

    if text.startswith("```"):
        first_newline = text.find("\n")

        if first_newline != -1:
            text = text[first_newline + 1:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

prompt = f"""
You are a university IT support assistant.

Student question:
{question}

Compressed context:
{compressed_context}

Return ONLY valid JSON with exactly this structure:
{{
    "problem": "string",
    "device": "string",
    "wifi_status": "string",
    "likely_cause": "string",
    "recommended_steps": ["string"],
    "escalate": false
}}
"""

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "system",
            "content": "You return structured IT support results."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print(response.message.content)

result = parse_json_response(response.message.content)

## WRITE the above output in an artifact called "state"
if result is None:
    print("The model did not return valid JSON.")
elif type(result) != dict:
    print("The model did not return a JSON object.")
else:
    with open("state.json", "w") as file:
        json.dump(result, file, indent=2)
## Update the rest of the code so that it uses the "state" artifact as part of the context. 
## It is important to ensure that the model uses only the relevant parts from the "state" artifact and not the entire artifact.
## For this, you may have to think of a good structure for the "state" artifact and how to use it in the context.

    with open("state.json", "r") as file:
        state = json.load(file)

    state_context = (
        "Problem: " + str(state.get("problem", question)) + "\n"
        "Device: " + str(state.get("device", "Windows laptop")) + "\n"
        "Wi-Fi status: " + str(state.get("wifi_status", "unknown")) + "\n"
        "Likely cause: " + str(state.get("likely_cause", "unknown")) + "\n"
        "Recommended steps: " + str(state.get("recommended_steps", []))
    )

    final_prompt = f"""
Use only the relevant state information below.
Write a short answer for the student.

Student question:
{question}

State information:
{state_context}
"""

    final_response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": final_prompt
            }
        ]
    )

    print(final_response.message.content)

diagnostic_context = {
    "problem": question,
    "device": "Windows laptop",
    "wifi_status": "operational"
}

report_context = {
    "total_wifi_cases": 37,
    "resolved_cases": 29,
    "unresolved_cases": 8
}

def classify_task(question_text):
    prompt = f"""
Classify this task as DIAGNOSE or REPORT.
DIAGNOSE means helping a student solve a specific IT problem.
REPORT means preparing an administrator report about many cases.

Question:
{question_text}

Return only one word: DIAGNOSE or REPORT.
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    task = response.message.content.strip().upper()

    if "REPORT" in task:
        return "REPORT"

    return "DIAGNOSE"


task = classify_task(question)

if task == "REPORT":
    active_context = report_context
else:
    active_context = diagnostic_context

print("Task:", task)
print("Active context:", active_context)
