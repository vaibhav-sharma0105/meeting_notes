from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from database import get_session
from services.rag import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest, session: Session = Depends(get_session)):
    answer = answer_question(session, req.query)
    return ChatResponse(answer=answer)
