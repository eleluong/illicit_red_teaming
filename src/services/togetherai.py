from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=os.getenv("TOGETHER_API_KEY"),
)
