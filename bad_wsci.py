## This file is a bad way of managing context. 

from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""


context = ""

for file in Path("knowledge").glob("*.txt"):
    context += file.read_text()
    context += "\n\n"

## Make a call to Qwen with student's question and the context from the knowledge base.
prompt = f"""
You are a university IT support assistant.
Answer the student's question using the university knowledge below.

Student question:
{question}

University knowledge:
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

## Just for fun, print the total length of the context
print(
    "Context characters:",
    len(context)
)

## Print the response from Qwen
print(response.message.content)