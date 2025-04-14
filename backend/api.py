from fastapi import FastAPI, HTTPException, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from custom_crew import CustomAgent, CustomTask, CustomCrew
from tools import process_pdf, summarize_text, generate_audio
from langchain_community.llms import LlamaCpp
import os
import time
from dotenv import load_dotenv
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi.responses import FileResponse

load_dotenv()

app = FastAPI()

# Configure Llama model from environment variables
model_path = os.getenv("MODEL_PATH", "./models/llama-2-7b.Q4_K_M.gguf")
gpu_layers = int(os.getenv("GPU_LAYERS", "40"))

print(f"🔍 CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', 'Not Set')}")
print(f"🔍 Initializing LlamaCpp with {gpu_layers} GPU layers on model: {model_path}")

# Add very verbose initialization to debug GPU usage
llama_llm = LlamaCpp(
    model_path=model_path,
    temperature=0.7,
    max_tokens=2000,
    n_ctx=2048,
    n_gpu_layers=gpu_layers,
    n_batch=512,
    f16_kv=True,            # Use half-precision for key/value cache
    verbose=True,           # Enable verbose mode to see which layers go to GPU
)

print("✅ LlamaCpp model initialized")

print("\n")
print("="*50)
print("🔍 GPU USAGE DIAGNOSTICS:")
print(f"GPU_LAYERS set to: {gpu_layers}")
print(f"CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', 'Not Set')}")

# Test GPU load using simple PyTorch test
try:
    import torch
    print(f"PyTorch CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"PyTorch CUDA device: {torch.cuda.get_device_name(0)}")
        # Create small tensor on GPU to verify functionality
        x = torch.rand(10, 10).cuda()
        print("✅ Successfully created tensor on GPU")
except ImportError:
    print("PyTorch not installed, skipping GPU test")
except Exception as e:
    print(f"❌ GPU test failed: {e}")

print("="*50)
print("\n")

print("\n🚀 Starting FastAPI server...")

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

# Create audio directory
AUDIO_DIR = UPLOAD_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
async def search(request: SearchRequest):
    # Check cache
    if request.query in cache:
        return Response(content=cache[request.query], media_type="text/plain")

    try:
        print(f"🔍 Starting search for: '{request.query}'")
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
0: <Full Paper Title> - <Paper Link>
1: <Full Paper Title> - <Paper Link>
2: <Full Paper Title> - <Paper Link>
3: <Full Paper Title> - <Paper Link>
4: <Full Paper Title> - <Paper Link>
""",
            expected_output="List of papers with titles and links in the specified format",
            agent=researcher,
            tools=["process_pdf"]
        )
        crew = CustomCrew(
            tasks=[search_task],
            agents=[researcher]
        )
        
        print(f"🧠 Running LLM inference for search query: '{request.query}'")
        start_time = time.time()
        outputs = crew.kickoff(inputs={"query": request.query})
        end_time = time.time()
        print(f"⏱️ Search completed in {end_time - start_time:.2f} seconds")
        
        # Extract the final string from the response
        final_result = list(outputs.values())[0]
        print(f"🔍 Raw search result: {final_result[:200]}...")
        
        lines = [l.strip() for l in final_result.split("\n") if l.strip()]
        papers = []
        
        for line in lines:
            print(f"Processing line: {line}")
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
        
        print(f"📄 Parsed {len(papers)} papers")
        
        if not papers:
            # Generate default response if parsing failed
            default_response = "0: Sample Paper Title - https://arxiv.org/abs/sample\n"
            default_response += "1: Another Paper Title - https://arxiv.org/abs/sample2\n"
            default_response += "2: Third Paper Title - https://arxiv.org/abs/sample3\n"
            default_response += "3: Fourth Paper Title - https://arxiv.org/abs/sample4\n"
            default_response += "4: Fifth Paper Title - https://arxiv.org/abs/sample5"
            print("⚠️ No papers parsed, returning default response")
            return Response(content=default_response, media_type="text/plain")
        
        cache["active_results"] = papers
        # Return both title and link to frontend
        minimal = [f"{p['index']}: {p['title']} - {p['link']}" for p in papers]
        result = "\n".join(minimal)  # Fix the syntax error here
        cache[request.query] = result
        print(f"✅ Returning search result: {result[:100]}...")
        return Response(content=result, media_type="text/plain")
        
    except Exception as e:
        import traceback
        print(f"❌ Error in search endpoint: {str(e)}")
        print(traceback.format_exc())
        # Return a fallback response so the frontend doesn't break
        fallback = "0: Error retrieving papers - please try again\n"
        return Response(content=fallback, media_type="text/plain")

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
Return in around 100 words only the paragraph with no extra text
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
    
    # Return the ID with the summary for frontend tracking
    return Response(content=f"{file_id}:{final_summary}", media_type="text/plain")

@app.post("/summarize-direct")
async def summarize_direct(request: DirectPaperRequest):
    paper_id = request.paper_id.strip()
    
    # Generate unique ID for this summary
    summary_id = str(uuid4())
    
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
        Return in around 100 words only the paragraph with no extra text
Provide a short, plain text overview with no disclaimers, references, or extra formatting.
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
    final_summary = list(outputs.values())[0].strip()
    
    # Store in cache with both the paper_id and a unique summary_id
    cache[paper_id] = final_summary
    cache[summary_id] = final_summary
    
    # Return the ID with the summary
    return Response(content=f"{summary_id}:{final_summary}", media_type="text/plain")

# Add a new endpoint to store summaries directly
@app.post("/store-summary/{summary_id}")
async def store_summary(summary_id: str, request: dict):
    if "summary" in request:
        cache[summary_id] = request["summary"]
        return Response(content="Summary stored", media_type="text/plain")
    else:
        raise HTTPException(status_code=400, detail="No summary provided")

@app.get("/summarize/{paper_index}")
async def summarize(paper_index: int):
    if "active_results" not in cache:
        raise HTTPException(status_code=404, detail="No papers in cache.")
    papers = cache["active_results"]
    if paper_index < 0 or paper_index >= len(papers):
        raise HTTPException(status_code=404, detail="Index out of range.")
    link = papers[paper_index]["link"]
    title = papers[paper_index]["title"]

    writer = CustomAgent(
        role="Technical Writer",
        goal="Write concise summaries of research papers",
        backstory="PhD in Computer Science with expertise in summarization.",
        tools=[summarize_text],
        llm=llama_llm
    )
    summarize_task = CustomTask(
        description=f"""Summarize the paper titled "{title}" from {link}.
        Return in around 100 words only the paragraph with no extra text
Provide a short, plain text overview with no disclaimers, references, or extra formatting.
""",
        expected_output="A concise summary paragraph about the paper",
        agent=writer,
        tools=["summarize_text"]
    )
    crew = CustomCrew(
        tasks=[summarize_task],
        agents=[writer]
    )
    outputs = crew.kickoff(inputs={"paper_id": link})
    # Extract the final string from the response
    raw_summary = list(outputs.values())[0]
    
    # Clean up the summary by removing references, citations, and formatting artifacts
    final_summary = clean_summary(raw_summary.strip())

    # Store in cache
    cache[paper_index] = final_summary
    return Response(content=final_summary, media_type="text/plain")

# Remove the audio generation cache - always generate new audio files
@app.post("/audio/{paper_id}")
@app.get("/audio/{paper_id}")  # Keep GET for backward compatibility
async def get_audio(paper_id: str):
    # Try to convert to int for backwards compatibility with search results
    try:
        numeric_id = int(paper_id)
        if numeric_id in cache:
            summary_text = cache[numeric_id]
        else:
            # If not found, check if the string ID exists in cache
            if paper_id in cache:
                summary_text = cache[paper_id]
            else:
                raise HTTPException(status_code=404, detail="No summary found. Summarize first.")
    except ValueError:
        # Handle as string ID
        if paper_id in cache:
            summary_text = cache[paper_id]
        else:
            raise HTTPException(status_code=404, detail="No summary found. Summarize first.")
    
    # Set a consistent path for audio files
    audio_file = f"uploads/audio/audio_{paper_id}.mp3"
    output_path = Path(audio_file)
    
    # Always delete the existing audio file to force regeneration
    if output_path.exists():
        try:
            output_path.unlink()
            print(f"Deleted existing audio file: {output_path}")
        except Exception as e:
            print(f"Warning: Could not delete existing audio file: {e}")
    
    try:
        print(f"Generating new audio for paper ID: {paper_id}")
        
        # Always generate a new audio file
        try:
            from audio_generator import check_espeak, install_instructions, generate_audio_file
            
            if not check_espeak():
                instructions = install_instructions()
                error_msg = f"Missing dependency: espeak not found. {instructions}"
                raise HTTPException(status_code=500, detail=error_msg)
            
            # Generate the audio file
            generate_audio_file(summary_text, str(output_path))
        except ImportError:
            # If audio_generator.py doesn't exist, try direct TTS import
            try:
                from TTS.api import TTS
                tts = TTS(model_name="tts_models/en/ljspeech/vits", gpu=False)
                tts.tts_to_file(text=summary_text[:2000], file_path=str(output_path))
            except ImportError:
                raise HTTPException(
                    status_code=500, 
                    detail="Text-to-Speech library not installed. Run 'pip install TTS' to install."
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"TTS error: {str(e)}"
                )
    except HTTPException:
        raise  # Re-raise HTTPExceptions
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate audio: {str(e)}"
        )
    
    # Return the audio file with cache prevention headers
    return FileResponse(
        path=output_path, 
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"attachment; filename=audio_{paper_id}.mp3",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            # Add a random value to prevent any caching
            "ETag": f"\"{uuid4()}\"", 
        }
    )

# Helper function to clean up summaries
def clean_summary(raw_text: str) -> str:
    # Remove reference sections
    if "[REFERENCES]" in raw_text:
        raw_text = raw_text.split("[REFERENCES]")[0]
    
    # Remove any URLs, citations, and other common artifacts
    import re
    raw_text = re.sub(r'http[s]?://\S+', '', raw_text)  # Remove URLs
    raw_text = re.sub(r'\[\d+\]', '', raw_text)         # Remove citations like [1]
    raw_text = re.sub(r'\n+', ' ', raw_text)            # Replace line breaks with spaces
    
    # Remove any remaining formatting markers
    markers_to_remove = ["[SUMMARY]", "[ABSTRACT]", "Summary:", "Abstract:"]
    for marker in markers_to_remove:
        raw_text = raw_text.replace(marker, "")
    
    return raw_text.strip()

@app.get("/health")
async def health_check():
    return Response(content="ok", media_type="text/plain")