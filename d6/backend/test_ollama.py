import ollama

response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Explain what a 2-to-4 decoder does."
        }
    ]
)

print(response["message"]["content"])