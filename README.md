# MultAgent Research Paper Summarizer

A multi-agent system that uses LLMs to search for research papers, summarize them, and generate audio explanations.

## Overview

This project leverages the power of Large Language Models (LLMs) through a multi-agent architecture to perform complex research tasks:

1. **Search:** Find relevant research papers on arXiv based on user queries
2. **Summarize:** Generate concise, informative summaries of research papers
3. **Audio:** Convert summaries to speech for audio consumption

Despite using a single LLM (Llama-2), the system implements a multi-agent architecture where different agents specialize in specific tasks.

## Architecture

### Multi-Agent System

The system employs specialized agents through the CrewAI framework:

- **Research Analyst Agent**: Searches for papers and extracts key information
- **Technical Writer Agent**: Transforms complex academic content into clear summaries
- **Audio Creator Agent**: Converts summaries into spoken explanations

Each agent has:
- **Role**: Specialized function within the system
- **Goal**: Clear objective that drives decision-making
- **Backstory**: Persona that shapes reasoning approach
- **Tools**: Specific capabilities (e.g., PDF processing, summarization)

### Component Overview

- **Backend**: FastAPI server running agents and handling API requests
- **Frontend**: React/MUI interface for user interactions
- **LLM**: Llama-2 7B quantized model for all agent reasoning

## Setup Instructions

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/MohakSomani/MultAgent-Research-Paper-Summarizer.git
   cd MultAgent-Research-Paper-Summarizer
   ```

2. Run the application with the provided script:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

   The script will:
   - Check for GPU availability
   - Clean Docker environment (containers, images)
   - Build and start Docker containers
   - Download the LLM if not present
   - Display logs

3. Access the application:
   - Frontend: http://localhost:5174
   - Backend API: http://localhost:8001

### Option 2: Local Setup

For development or customization:

1. Clone the repository:
   ```bash
   git clone https://github.com/MohakSomani/MultAgent-Research-Paper-Summarizer.git
   cd MultAgent-Research-Paper-Summarizer
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Download the model:
   ```bash
   mkdir -p models
   python download_model.py
   ```

4. Start the backend:
   ```bash
   uvicorn api:app --reload
   ```

5. Install and start the frontend:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

## Usage

1. **Search for Papers**:
   - Enter a research topic in the search field
   - System will retrieve relevant papers from arXiv

2. **Generate Summaries**:
   - Select a paper from the results
   - Click "Summarize" to generate a concise summary
   - Review the summary in the interface

3. **Upload Papers** (Alternative):
   - Use the "Upload PDF" option to directly upload papers
   - Enter arXiv IDs or URLs in the "Enter Paper URL/ID" field

## Implementation Details

### Multi-Agent System Implementation

The multi-agent architecture is implemented through:

1. **Custom Agent Definitions** (`custom_crew.py`):
   ```python
   class CustomAgent:
       # Role-specific agent configuration
       # Each agent has particular expertise and capabilities
   ```

2. **Task Delegation** (`api.py`):
   ```python
   search_task = CustomTask(
       description="Find 5 recent papers about {query} on arXiv",
       expected_output="List of papers with titles, PDF URLs",
       agent=researcher,
       tools=["process_pdf"]
   )
   ```

3. **Specialized Tools** (`tools.py`):
   ```python
   @tool("PDF Processor")
   def process_pdf(pdf_path=None, arxiv_id=None):
       # Tool for processing PDFs
   ```

### How Multi-Agent Works with One LLM

While using a single LLM (Llama-2), the system creates a multi-agent architecture through:

1. **Agent Specialization**: Each agent has unique prompts, tasks, and tools
2. **Context Isolation**: Agents operate with isolated context, focusing on specific tasks
3. **Tool Integration**: Different capabilities through specialized tools for each role
4. **Sequential Processing**: Multi-stage workflow where each agent handles part of the pipeline

This approach allows the single LLM to effectively operate as multiple specialized agents, each focusing on a particular aspect of the overall task.

## Technical Stack

- **Backend**: FastAPI, Langchain, CrewAI
- **LLM**: Llama-2 (7B quantized)
- **Frontend**: React, Material UI
- **TTS**: TTS Library for audio generation
- **Research Tools**: arXiv API integration
- **Containerization**: Docker and Docker Compose
