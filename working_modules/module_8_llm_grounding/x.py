from openai import OpenAI

client = OpenAI(
  api_key="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"
)

response = client.responses.create(
  model="gpt-5-nano",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text);
