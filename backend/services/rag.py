from typing import List, Optional
from sqlmodel import Session, select
from models import TranscriptChunk
from services.intelligence import generate_embedding
from litellm import completion
from core.config import settings

def retrieve_context(session: Session, query: str, limit: int = 5) -> str:
    """
    Retrieves relevant chunks from the database based on vector similarity.
    """
    try:
        query_vec = generate_embedding(query)
        # pgvector l2_distance or cosine_distance
        # SQLModel/SQLAlchemy pgvector syntax:
        statement = select(TranscriptChunk).order_by(TranscriptChunk.embedding.cosine_distance(query_vec)).limit(limit)
        results = session.exec(statement).all()

        context_text = "\n\n".join([f"Speaker {c.speaker}: {c.text}" for c in results])
        return context_text
    except Exception as e:
        print(f"RAG Retrieval failed: {e}")
        return ""

def answer_question(session: Session, query: str) -> str:
    """
    Generates an answer to the user's question using RAG.
    """
    context = retrieve_context(session, query)

    if not context:
        return "I couldn't find any relevant meeting notes to answer your question."

    config = settings.get_llm_config()
    model_name = config.get("model", "gpt-4o")

    prompt = f"""
    You are MeetOps, an intelligent assistant for meeting notes.
    Use the following context from previous meetings to answer the user's question.
    If the answer is not in the context, say you don't know.

    Context:
    {context}

    User Question: {query}
    """

    try:
        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            api_key=config.get("api_key"),
            api_base=config.get("api_base")
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"
