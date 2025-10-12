import hashlib
import uuid

def normalize(data,source,question=None,answer=None):
    """Ensure every data/entry has same shape/schema"""
    text=''
    if question and answer:
        text = f"Q: {question.strip()}\nA: {answer.strip()}"
    elif "question" in data and "answer" in data:
        text = f"Q: {data['question'].strip()}\nA: {data['answer'].strip()}"
    elif data.get("content"):
        text = data["content"].strip()

    # Normalize whitespace (remove extra spaces/newlines inside the text)
    text = " ".join(text.split())
    
    return{
        "id":str(uuid.UUID(hashlib.md5(text.encode('utf-8')).hexdigest()[:32])), # Use MD5 hash of text as ID, have to use uuid format for Qdrant, otherwise Qdrant will create its own ID
        "question":question or data.get("question") or "",
        "answer":answer or data.get("answer") or "",
        "content":text,
        "source":source or data.get("source") or "unknown"
    }
    
