import streamlit as st
from groq import Groq


MODEL_NAME = "openai/gpt-oss-120b"


def get_groq_client():
    api_key = st.secrets.get(
        "GROQ_API_KEY",
        "",
    )

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured in Streamlit secrets."
        )

    return Groq(
        api_key=api_key
    )


def generate_answer(
    system_prompt: str,
    user_prompt: str,
) -> str:

    client = get_groq_client()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.2,
        max_completion_tokens=500,
    )

    return response.choices[0].message.content.strip()
