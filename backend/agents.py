from custom_crew import CustomAgent
from tools import process_pdf, summarize_text, generate_audio
import os
from dotenv import load_dotenv
from langchain_community.llms import LlamaCpp

load_dotenv()

# Disable LiteLLM entirely
os.environ["CREWAI_DISABLE_LITELLM"] = "true"  # Fully bypass LiteLLM

# Configure Llama model
llama_llm = LlamaCpp(
    model_path="./models/llama-2-7b.Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=2000,
    n_ctx=2048,
    n_gpu_layers=40,  # Set to 0 for CPU-only
    n_batch=512,
    verbose=False
)

class ResearchAgents:
    def researcher(self):
        return CustomAgent(
            role="Senior Research Analyst",
            goal="Find and analyze cutting-edge research papers",
            backstory="Expert researcher with 10 years' experience in ML paper analysis.",
            tools=[process_pdf],
            llm=llama_llm,
            verbose=True
        )

    def writer(self):
        return CustomAgent(
            role="Technical Writer",
            goal="Write concise summaries of research papers",
            backstory="PhD in Computer Science with expertise in summarization.",
            tools=[summarize_text],
            llm=llama_llm,
            verbose=True
        )

    def podcaster(self):
        return CustomAgent(
            role="Podcast Producer",
            goal="Create engaging audio summaries",
            backstory="Audio engineer with 5 years' TTS experience.",
            tools=[generate_audio],
            llm=llama_llm,
            verbose=True
        )