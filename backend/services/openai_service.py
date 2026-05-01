from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def complete(system, user):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def complete_json(system, user):
    response = complete(system, user)

    try:
        return json.dumps(json.loads(response))
    except:
        return json.dumps({
            "simple": response,
            "professional": response,
            "native": response
        })