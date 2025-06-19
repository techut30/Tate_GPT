from backend.rag.retriever import search
from backend.llm.llm_client import build_prompt, query_llm

question = "what is money?"
results = search(question, top_k=4)

chunks = [text for text, _ in results]
prompt = build_prompt(question, chunks)
answer = query_llm(prompt)

print("Answer:\n", answer)
