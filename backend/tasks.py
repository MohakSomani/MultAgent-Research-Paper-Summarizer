from custom_crew import CustomAgent, CustomTask
from langchain_community.llms import LlamaCpp
from tools import process_pdf, summarize_text, generate_audio
from dotenv import load_dotenv

load_dotenv()

# Configure Llama model
llama_llm = LlamaCpp(
    model_path="./models/llama-2-7b.Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=2000,
    n_ctx=2048,
    n_gpu_layers=40,
    verbose=False
)

def search_task():
    researcher = CustomAgent(
        role="Senior Research Analyst",
        goal="Find and analyze cutting-edge research papers",
        backstory="Expert researcher with 10 years' experience in ML paper analysis.",
        tools=[process_pdf],
        llm=llama_llm
    )
    return CustomTask(
        description="Find 5 recent papers about {query} on arXiv",
        expected_output="List of papers with titles, PDF URLs, and publication dates",
        agent=researcher,
        tools=["process_pdf"]
    )

def summarize_task():
    writer = CustomAgent(
        role="Technical Writer",
        goal="Write concise summaries of research papers",
        backstory="PhD in Computer Science with expertise in summarization.",
        tools=[summarize_text],
        llm=llama_llm
    )
    return CustomTask(
        description="Summarize the paper with ID: {paper_id}",
        expected_output="3-paragraph technical summary in markdown format",
        agent=writer,
        tools=["summarize_text"]
    )

def podcast_task():
    podcaster = CustomAgent(
        role="Podcast Producer",
        goal="Create engaging audio summaries",
        backstory="Audio engineer with 5 years' TTS experience.",
        tools=[generate_audio],
        llm=llama_llm
    )
    return CustomTask(
        description="Generate a podcast script for the summary",
        expected_output="Path to generated MP3 file",
        agent=podcaster,
        tools=["generate_audio"]
    )