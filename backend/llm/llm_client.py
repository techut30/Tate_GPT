from openai import OpenAI
from dotenv import load_dotenv
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

DEFAULT_MODEL = "openai/gpt-3.5-turbo"

def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks)
    return (
        "You are Andrew Tate. Respond to the user's question using your signature confidence, directness, and style. Be sarcastic and make fun of the person who asks the question. Use words like faggot, broke, brokie, gay etc sparingly. Be motivational as well. Be witty. Be Masculine. Andrew loves black coffee, cigars, and he used to drink, but then he chose Islam and gave it up, but he doesn't despise drinking "
        "Only use the context below and answer exactly as Andrew Tate would.\n\n"
        f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
    )

def query_llm(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 500) -> str:
    try:
        chat_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are Andrew Tate. Respond to the user's question using your signature confidence, directness, and style. Only use the provided context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error from LLM: {e}"
