from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import shutil
import json

from controller import decide_route
from agents.pdf_rag_agent import query_rag_agent
from agents.web_search_agent import query_web_search_agent
from agents.arxiv_agent import query_arxiv_agent
from utils import synthesize_answer 

load_dotenv()

app = FastAPI(title="Multi-Agent AI System")

# --- Global Exception Handler ---
# This catches any unexpected server errors and prevents the app from crashing.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An internal server error occurred: {exc}"},
    )

UPLOAD_DIR = "uploads"
LOG_FILE = "logs/controller_log.jsonl"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Handles PDF uploads."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Trigger pre-processing/embedding for the RAG agent
    from agents.pdf_rag_agent import get_vector_store
    get_vector_store(file_path)

    return {"filename": file.filename, "detail": "File uploaded and processed successfully."}

@app.post("/ask/")
async def ask_system(query: str = Form(...), filename: str = Form(None)):
    """Main endpoint to ask the multi-agent system."""
    pdf_uploaded = filename is not None and filename != "null"
    
    # 1. Get routing decision from Controller
    controller_decision = decide_route(query, pdf_uploaded)
    agents_to_call = controller_decision.get("agents", [])
    
    # 2. Execute the chosen agents
    context_data = ""
    retrieved_docs_metadata = []

    for agent in agents_to_call:
        if agent == "PDF_RAG_AGENT" and pdf_uploaded:
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(file_path):
                context, metadata = query_rag_agent(file_path, query)
                context_data += f"\n\n--- Context from PDF Document ---\n{context}"
                retrieved_docs_metadata.append({"agent": "PDF_RAG_AGENT", "metadata": metadata})

        elif agent == "WEB_SEARCH_AGENT":
            context, metadata = query_web_search_agent(query)
            context_data += f"\n\n--- Context from Web Search ---\n{context}"
            retrieved_docs_metadata.append({"agent": "WEB_SEARCH_AGENT", "metadata": metadata})

        elif agent == "ARXIV_AGENT":
            context, metadata = query_arxiv_agent(query)
            context_data += f"\n\n--- Context from ArXiv ---\n{context}"
            retrieved_docs_metadata.append({"agent": "ARXIV_AGENT", "metadata": metadata})
            
    # 3. Synthesize the final answer using the collected context
    final_answer = synthesize_answer(query, context_data)
    
    return {
        "query": query,
        "controller_decision": controller_decision,
        "final_answer": final_answer,
        "retrieved_docs": retrieved_docs_metadata
    }

@app.get("/logs/")
async def get_logs():
    """Endpoint to retrieve controller logs."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        logs = [json.loads(line) for line in f]
    return logs
