import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

def generate_sentence(system_prompt: str, input_data: str) -> str:

    sentence = client.responses.create(
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_data}
        ],
        model="gpt-5.2",
        reasoning={
            "effort": "high"        }
    )
    print(sentence)
    return sentence.output_text
