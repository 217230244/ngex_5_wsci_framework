from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    ##Use only the files that are relevant to the question.
    "knowledge/wifi_setup.txt",
    "knowledge/password_changes.txt"
]


context = ""

## Write a for loop to go through all the files in selected_files and read their contents into the context variable.
for filename in selected_files:
    context += Path(filename).read_text()
    context += "\n\n"

## Call Qwen with the student's question and the context you created above.
prompt = f"""
You are a university IT support assistant.
Answer the student's question using only the selected university knowledge below.

Student question:
{question}

Selected university knowledge:
{context}
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


print(
    "Context characters:",
    len(context)
)
print(response.message.content)