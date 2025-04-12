from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from custom_crew import CustomAgent, CustomTask, CustomCrew
from tools import process_pdf, summarize_text
from langchain_community.llms import LlamaCpp
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure Llama model
llama_llm = LlamaCpp(
    model_path="./models/llama-2-7b.Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=2000,
    n_ctx=2048,
    n_gpu_layers=40,
    verbose=False
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
async def search(request: SearchRequest):
    researcher = CustomAgent(
        role="Senior Research Analyst",
        goal="Find and analyze cutting-edge research papers",
        backstory="Expert researcher with 10 years' experience in ML paper analysis.",
        tools=[process_pdf],
        llm=llama_llm
    )
    search_task = CustomTask(
        description="Find 5 recent papers about {query} on arXiv",
        expected_output="List of papers with titles, PDF URLs, and publication dates",
        agent=researcher,
        tools=["process_pdf"]
    )
    crew = CustomCrew(
        tasks=[search_task],
        agents=[researcher]
    )
    outputs = crew.kickoff(inputs={"query": request.query})
    return {"result": outputs}

@app.get("/summarize/{paper_id}")
async def summarize(paper_id: str):
    writer = CustomAgent(
        role="Technical Writer",
        goal="Write concise summaries of research papers",
        backstory="PhD in Computer Science with expertise in summarization.",
        tools=[summarize_text],
        llm=llama_llm
    )
    summarize_task = CustomTask(
        description="Summarize the paper with ID: {paper_id}",
        expected_output="3-paragraph technical summary in markdown format",
        agent=writer,
        tools=["summarize_text"]
    )
    crew = CustomCrew(
        tasks=[summarize_task],
        agents=[writer]
    )
    outputs = crew.kickoff(inputs={"paper_id": paper_id})
    return {"summary": outputs}

@app.get("/health")
async def health_check():
    return {"status": "ok"}