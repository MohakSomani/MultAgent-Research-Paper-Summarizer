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

### Prerequisites

- Git
- Docker and Docker Compose (for Docker setup)
- Python 3.10+ (for local setup)
- Node.js 18+ (for local frontend)
- NVIDIA GPU (optional, for faster inference)

### Option 1: Docker (NOT WORKING PROPERLY)

The easiest way to run the application is using Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MultAgent-Research-Paper-Summarizer.git
   cd MultAgent-Research-Paper-Summarizer
   ```

2. Make the run script executable and execute it:
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
   npm install  # Only needed first time
   npm run dev
   ```

5. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## Usage

### Paper Search Pipeline

1. Enter your research topic in the search field
2. Click "Search" to find recent papers on the topic
3. View the list of papers with titles and links
4. Pipeline: `User Query → API → Research Agent → arXiv → Results`

### Paper Summarization Pipeline

1. Select a paper from the search results using the dropdown
2. Click "Summarize" to generate a concise summary
3. Review the summary in the interface
4. Pipeline: `Paper Selection → API → Writer Agent → Summary Generation → Display`

### Audio Generation Pipeline

1. After generating a summary, click "Generate Podcast"
2. Wait for the audio to be processed (always creates fresh audio)
3. Use the audio player to listen to the summary
4. Pipeline: `Summary Text → API → TTS Engine → Audio File → Audio Playback`

### PDF Upload Pipeline

1. Navigate to the "Upload PDF or Enter Paper" section
2. Upload your PDF file
3. System will process and extract text from the PDF
4. Writer agent generates a concise summary
5. Pipeline: `PDF Upload → File Storage → Text Extraction → Writer Agent → Summary`

### Direct arXiv URL/ID Pipeline

1. Navigate to the "Upload PDF or Enter Paper" section
2. Enter an arXiv URL or paper ID
3. Click "Summarize" to process the paper
4. The system will fetch the paper from arXiv and summarize it
5. Pipeline: `arXiv ID → API → arXiv Fetch → Writer Agent → Summary`

## Implementation Details

### Backend Pipeline

The backend system consists of these key components working together:

1. **FastAPI Server (api.py)**  
   - Handles HTTP endpoints and request routing
   - Manages caching for performance optimization
   - Coordinates agent workflows
   - File structure:
     ```
     backend/
     ├── api.py           # Main API endpoints
     ├── custom_crew.py   # Agent orchestration
     ├── tools.py         # Agent tools implementation
     ├── audio_generator.py # TTS functionality
     └── requirements.txt # Dependencies
     ```

2. **Agent System (custom_crew.py)**  
   - Implements agent specialization via roles
   - Manages tool access and context isolation
   - Enables multi-step agent workflows
   - Example workflow:
     ```
     Research Query → Research Agent → arXiv Processing → 
     Writer Agent → Summary Generation → Audio Agent → Speech Synthesis
     ```

3. **Tool Integration (tools.py)**  
   - `process_pdf`: Searches arxiv and processes papers
   - `summarize_text`: Generates concise paper summaries
   - `generate_audio`: Converts text to spoken audio

4. **Audio Generation (audio_generator.py)**
   - Connects to TTS library
   - Handles text preprocessing for audio
   - Generates MP3 files
   - Flow: `Summary Text → TTS Engine → Audio File`

### Frontend Architecture

The React frontend provides an intuitive interface:

1. **Main Components**
   - `App.jsx`: Main application container
   - `PaperSearch.jsx`: Search interface
   - `FileUpload.jsx`: PDF and URL submission
   - `AudioPlayer.jsx`: Audio playback

2. **API Integration**
   - RESTful communication with backend
   - Proper error handling and loading states
   - File structure:
     ```
     frontend/
     ├── src/
     │   ├── App.jsx            # Main application
     │   ├── api.js             # API client functions
     │   ├── components/        # UI components  
     │   │   ├── PaperSearch.jsx
     │   │   ├── FileUpload.jsx
     │   │   └── AudioPlayer.jsx
     │   └── main.jsx           # Entry point
     ├── package.json           # Dependencies
     └── vite.config.js         # Build configuration
     ```

### Environmental Considerations

1. **GPU Acceleration**
   - The system automatically detects NVIDIA GPUs
   - Configures Llama.cpp to use GPU layers when available
   - Falls back to CPU-only mode when no GPU is present

2. **Docker vs Local**
   - Docker provides isolation and dependency management
   - Local setup allows for easier development and debugging
   - Both approaches use the same core code and workflows

3. **File Storage**
   - Uploads stored in `backend/uploads/`
   - Audio files in `backend/uploads/audio/`
   - Models in `backend/models/`

## Technical Stack

- **Backend**: FastAPI, Langchain, CrewAI
- **LLM**: Llama-2 (7B quantized)
- **Frontend**: React, Material UI, Vite
- **TTS**: TTS Library for audio generation
- **Research Tools**: arXiv API integration
- **Containerization**: Docker and Docker Compose
