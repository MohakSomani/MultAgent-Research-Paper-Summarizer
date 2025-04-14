# MultAgent Research Paper Summarizer

A multi-agent system that uses Large Language Models to search for research papers, create concise summaries, and generate audio explanations.

## Overview

This project leverages the power of Large Language Models (LLMs) through a multi-agent architecture to perform complex research tasks:

1. **Search:** Find relevant research papers on arXiv based on user queries
2. **Summarize:** Generate concise, informative summaries of research papers
3. **Audio:** Convert summaries to speech for audio consumption

Despite using a single LLM (Llama-2), the system implements a multi-agent architecture where different agents specialize in specific tasks and work together to achieve complex workflows.

## Features

- 🔍 **Paper Search**: Search for recent scientific papers on arXiv by topic
- 📝 **Smart Summarization**: Generate concise, readable summaries of complex research papers
- 🎧 **Audio Generation**: Convert summaries to spoken audio for listening on the go
- 📄 **PDF Upload**: Upload PDFs directly for summarization
- 🔗 **Direct URL Processing**: Enter arXiv links or IDs to process papers

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
- **TTS**: Text-to-speech library for audio generation

## Setup Instructions

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MultAgent-Research-Paper-Summarizer.git
   cd MultAgent-Research-Paper-Summarizer
   ```

2. Run the application with the provided script:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

   The script will:
   - Check for GPU availability
   - Create necessary directories
   - Build and start Docker containers
   - Download the LLM if not present
   - Display logs

3. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

### Option 2: Local Setup

For development or systems without Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MultAgent-Research-Paper-Summarizer.git
   cd MultAgent-Research-Paper-Summarizer
   ```

2. Setup and activate local environment:
   ```bash
   chmod +x LOCAL_setup.sh
   ./LOCAL_setup.sh
   ```

3. Run the backend:
   ```bash
   chmod +x LOCAL_run_backend.sh
   ./LOCAL_run_backend.sh
   ```

4. In a separate terminal, run the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## Usage

### Paper Search

1. Enter your research topic in the search field
2. Click "Search" to find recent papers on the topic
3. View the list of papers with titles and links

### Generate Summaries

1. Select a paper from the search results using the dropdown
2. Click "Summarize" to generate a concise summary
3. Review the summary in the interface

### Create Audio Explanations

1. After generating a summary, click "Generate Podcast"
2. Wait for the audio to be processed
3. Use the audio player to listen to the summary

### Upload PDF or Use Direct URL

1. Navigate to the "Upload PDF or Enter Paper" section
2. Either upload a PDF file or enter an arXiv URL/ID
3. Click "Summarize" to process the paper
4. Generate audio as needed using the "Generate Podcast" button

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

## Backend Architecture

### Core Components

The backend system consists of these key components working together:

1. **FastAPI Server (api.py)**  
   - Exposes HTTP endpoints for search, summarization, and PDF upload
   - Handles request validation and response formatting
   - Implements a caching system for improved performance
   - Routes requests to appropriate agent workflows

2. **Custom Agent Framework (custom_crew.py)**  
   - Defines the `CustomAgent` class that encapsulates agent behavior
   - Implements `CustomTask` for specific task execution
   - Creates `CustomCrew` for orchestrating multi-agent workflows
   - Manages prompting logic and context passage between agents

3. **Specialized Tools (tools.py)**  
   - `process_pdf`: Extracts information from PDF papers or arxiv links
   - `summarize_text`: Uses LLM to generate concise summaries
   - `generate_audio`: Converts text to speech using TTS

4. **LLM Integration**  
   - Uses `LlamaCpp` for local inference without API dependencies
   - Configures model parameters via environment variables
   - Implements proper context management for optimal results

### Workflow Explanation

Here's how the system processes typical requests:

1. **Paper Search Flow**:
   ```
   User Query → FastAPI → Research Analyst Agent → 
   process_pdf tool → arXiv API → Results Cache → 
   Formatted Response
   ```

2. **Summarization Flow**:
   ```
   Paper ID → FastAPI → Technical Writer Agent → 
   summarize_text tool → Paper Content → LLM → 
   Formatted Summary → Response
   ```

3. **PDF Upload Flow**:
   ```
   PDF File → FastAPI → File Storage → 
   Technical Writer Agent → summarize_text tool → 
   LLM → Formatted Summary → Response
   ```

4. **Audio Generation Flow**:
   ```
   Summary Text → FastAPI → TTS Library → 
   Audio File → Audio Response
   ```

### Agent Intelligence

The intelligence of the system comes from:

1. **Specialized Prompting**: Each agent receives role-specific instructions
2. **Tool Integration**: Agents have access to specific external capabilities
3. **Context Management**: Information flows between tasks via structured context
4. **Task Formalization**: Clear task definitions with expected outputs

### Caching Strategy

The backend implements an efficient in-memory caching system:

1. **Query Results**: Previous search results are cached by query string
2. **Paper Summaries**: Generated summaries are cached by paper index/ID
3. **Direct Paper Cache**: Papers submitted via URL/ID are cached by identifier

This dramatically improves performance for repeated requests and enables more responsive user experiences.

## Technical Stack

- **Backend**: FastAPI, Langchain, CrewAI
- **LLM**: Llama-2 (7B quantized)
- **Frontend**: React, Material UI
- **TTS**: TTS Library for audio generation
- **Research Tools**: arXiv API integration
- **Containerization**: Docker and Docker Compose

## License

This project is licensed under the MIT License - see the LICENSE file for details.