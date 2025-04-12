from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from custom_crew import CustomAgent, CustomTask, CustomCrew
from tools import process_pdf, summarize_text
from langchain_community.llms import LlamaCpp
import os
from dotenv import load_dotenv
import shutil
from pathlib import Path
from uuid import uuid4

load_dotenv()

app = FastAPI()

# Configure Llama model from environment variables
model_path = os.getenv("MODEL_PATH", "./models/llama-2-7b.Q4_K_M.gguf")
gpu_layers = int(os.getenv("GPU_LAYERS", "40"))

llama_llm = LlamaCpp(
    model_path=model_path,
    temperature=0.7,
    max_tokens=2000,
    n_ctx=2048,
    n_gpu_layers=gpu_layers,
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

# In-memory cache
cache = {}

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
async def search(request: SearchRequest):
    # Check cache
    if request.query in cache:
        return cache[request.query]

    researcher = CustomAgent(
        role="Senior Research Analyst",
        goal="Find and analyze cutting-edge research papers",
        backstory="Expert researcher with 10 years' experience in ML paper analysis.",
        tools=[process_pdf],
        llm=llama_llm
    )
    search_task = CustomTask(
        description="""Find 5 recent papers about {query} on arXiv.
Return exactly 5 lines of output, numbered 0 through 4, each in this exact format with no extra text or disclaimers:
0: [LINK] <Paper Title> - <Paper Link>
1: [LINK] <Paper Title> - <Paper Link>
2: [LINK] <Paper Title> - <Paper Link>
3: [LINK] <Paper Title> - <Paper Link>
4: [LINK] <Paper Title> - <Paper Link>
""",
        expected_output="List of papers with titles and links in the specified format",
        agent=researcher,
        tools=["process_pdf"]
    )
    crew = CustomCrew(
        tasks=[search_task],
        agents=[researcher]
    )
    outputs = crew.kickoff(inputs={"query": request.query})
    # Extract the final string from the response
    final_result = list(outputs.values())[0]
    lines = [l.strip() for l in final_result.split("\n") if l.strip()]
    papers = []
    for line in lines:
        if line[0].isdigit() and ":" in line:
            idx_str, rest = line.split(":", 1)
            idx_str = idx_str.strip()
            rest = rest.strip()
            # e.g. "[LINK] Paper Title - https://arxiv.org/abs/..."
            if " - " in rest:
                title_part, link_part = rest.split(" - ", 1)
                papers.append({
                    "index": int(idx_str),
                    "title": title_part.replace("[LINK]", "").strip(),
                    "link": link_part.strip()
                })
    cache["active_results"] = papers
    # Return only index + title to frontend
    minimal = [f"{p['index']}: {p['title']}" for p in papers]
    cache[request.query] = "\n".join(minimal)
    return cache[request.query]

class DirectPaperRequest(BaseModel):
    paper_id: str

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Generate a unique filename
    file_id = str(uuid4())
    file_location = UPLOAD_DIR / f"{file_id}.pdf"
    
    # Save the uploaded file
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()
    
    # Process the PDF using the existing writer agent
    writer = CustomAgent(
        role="Technical Writer",
        goal="Write concise summaries of research papers",
        backstory="PhD in Computer Science with expertise in summarization.",
        tools=[summarize_text],
        llm=llama_llm
    )
    
    summarize_task = CustomTask(
        description=f"""Summarize the PDF paper located at: {file_location}.
Return only the following format with no extra text:
[SUMMARY]
<Summary Text>
""",
        expected_output="Summary of the paper in the specified format",
        agent=writer,
        tools=["summarize_text"]
    )
    
    crew = CustomCrew(
        tasks=[summarize_task],
        agents=[writer]
    )
    
    outputs = crew.kickoff(inputs={"paper_location": str(file_location)})
    # Extract the final string from the response
    final_summary = list(outputs.values())[0]
    
    # Store in cache with the file_id as key
    cache[file_id] = final_summary
    
    return final_summary

@app.post("/summarize-direct")
async def summarize_direct(request: DirectPaperRequest):
    paper_id = request.paper_id.strip()
    
    # Check cache
    if paper_id in cache:
        return cache[paper_id]
    
    # Process paper ID (could be arXiv ID or full URL)
    if "arxiv.org" in paper_id:
        # Extract the ID from the URL
        import re
        arxiv_id = re.search(r'(\d+\.\d+)', paper_id)
        if arxiv_id:
            paper_id = arxiv_id.group(1)
    
    # Create a writer agent to summarize the paper
    writer = CustomAgent(
        role="Technical Writer",
        goal="Write concise summaries of research papers",
        backstory="PhD in Computer Science with expertise in summarization.",
        tools=[summarize_text],
        llm=llama_llm
    )
    
    summarize_task = CustomTask(
        description=f"""Summarize the paper with ID: {paper_id}.
Return in almost 100 words only the following format with no extra text:
[SUMMARY]
<Summary Text>
""",
        expected_output="Summary of the paper in the specified format",
        agent=writer,
        tools=["summarize_text"]
    )
    
    crew = CustomCrew(
        tasks=[summarize_task],
        agents=[writer]
    )
    
    outputs = crew.kickoff(inputs={"paper_id": paper_id})
    # Extract the final string from the response
    final_summary = list(outputs.values())[0]
    
    # Store in cache
    cache[paper_id] = final_summary
    
    return final_summary

@app.get("/summarize/{paper_index}")
async def summarize(paper_index: int):
    if "active_results" not in cache:
        raise HTTPException(status_code=404, detail="No papers in cache.")
    papers = cache["active_results"]
    if paper_index < 0 or paper_index >= len(papers):
        raise HTTPException(status_code=404, detail="Index out of range.")
    link = papers[paper_index]["link"]

    writer = CustomAgent(
        role="Technical Writer",
        goal="Write concise summaries of research papers",
        backstory="PhD in Computer Science with expertise in summarization.",
        tools=[summarize_text],
        llm=llama_llm
    )
    summarize_task = CustomTask(
        description="""Summarize the paper with ID: {paper_id}.
Return in almost 100 words only the following format with no extra text:
[SUMMARY]
<Summary Text>
""",
        expected_output="Summary of the paper in the specified format",
        agent=writer,
        tools=["summarize_text"]
    )
    crew = CustomCrew(
        tasks=[summarize_task],
        agents=[writer]
    )
    outputs = crew.kickoff(inputs={"paper_id": link})
    # Extract the final string from the response
    final_summary = list(outputs.values())[0]

    # Store in cache
    cache[paper_index] = final_summary
    return final_summary  # Return formatted result as a plain string

@app.get("/health")
async def health_check():
    return "ok"  # Return as a plain string