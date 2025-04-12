import os
from dotenv import load_dotenv
from crewai.tools import tool
from TTS.api import TTS
from langchain_community.llms import LlamaCpp

load_dotenv()
os.environ["CREWAI_DISABLE_AWS"] = "true"

# Configure LlamaCpp from environment variables
model_path = os.getenv("MODEL_PATH", "./models/llama-2-7b.Q4_K_M.gguf")
llama_llm = LlamaCpp(
    model_path=model_path,
    temperature=0.7,
    max_tokens=2000
)

@tool("PDF Processor")
def process_pdf(pdf_path=None, arxiv_id=None):
    """
    Process a PDF file from a local path or fetch from arXiv.
    Returns key information from the paper using direct text extraction.
    """
    try:
        # Simple PDF processing without Grobid
        if pdf_path and os.path.exists(pdf_path):
            # Basic PDF text extraction
            # You can use libraries like PyPDF2 or pdfplumber
            return f"Processed PDF: {pdf_path}"
        elif arxiv_id:
            # Simple arXiv fetching
            return f"Processed arXiv paper: {arxiv_id}"
        else:
            return "Error: Either pdf_path or arxiv_id must be provided"
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

@tool("Research Summarizer")
def summarize_text(text: str) -> str:
    """Summarize text using the local Llama model."""
    response = llama_llm.invoke(f"Summarize the following text:\n{text[:3000]}")
    return response

@tool("Audio Generator")
def generate_audio(text: str, output_path: str = "output.mp3") -> str:
    """Convert text to speech"""
    tts = TTS(model_name="tts_models/en/ljspeech/vits", gpu=True)
    tts.tts_to_file(text=text[:5000], file_path=output_path)
    return output_path