import os
from dotenv import load_dotenv
from crewai.tools import tool
from grobid_client.grobid_client import GrobidClient
from TTS.api import TTS
from langchain_community.llms import LlamaCpp

load_dotenv()
os.environ["CREWAI_DISABLE_AWS"] = "true"

# Configure LlamaCpp for local usage
llama_llm = LlamaCpp(
    model_path="./models/llama-2-7b.Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=2000
)

@tool("PDF Processor")
def process_pdf(pdf_url: str) -> str:
    """Extract text from PDF using GROBID"""
    client = GrobidClient(
        config_path="./config/grobid-config.json",
        grobid_server="http://grobid:8070"  # Docker service name
    )
    doc = client.process("processFulltextDocument", pdf_url)
    return doc["body"]

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