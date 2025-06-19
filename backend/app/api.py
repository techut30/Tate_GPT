from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.rag.retriever import search
from backend.llm.llm_client import build_prompt, query_llm

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(req: QuestionRequest):
    top_chunks = search(req.question, top_k=3)
    prompt = build_prompt(req.question, [chunk for chunk, _ in top_chunks])
    answer = query_llm(prompt)
    return {"answer": answer}
