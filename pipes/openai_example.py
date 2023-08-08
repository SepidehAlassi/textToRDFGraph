import openai
openai.api_key = "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"

context = "Albert Einstein was a German-born theoretical physicist who developed the theory of relativity."
question = "Where was Albert Einstein born?"
response = openai.Completion.create(
  engine="gpt-3.5-turbo",
  prompt=f"Question answering:\nContext: {context}\nQuestion: {question}",
  max_tokens=50
)

answer = response.choices[0].text.strip()
print(answer)
