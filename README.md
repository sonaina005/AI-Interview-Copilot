# AI Technical Interview Copilot 🎯

An intelligent interview preparation system that analyzes your CV and job description to conduct personalized, adaptive mock interviews.

## Features

- 📄 **Smart Resume Analysis** — Extracts skills and identifies gaps compared to job requirements
- 🔍 **RAG-Powered Context** — Uses vector search to generate relevant, personalized questions
- 🎯 **Adaptive Questioning** — Generates technical questions based on your actual skills and the job description
- 💡 **Real-time Hints** — Provides helpful hints when answers need improvement
- 📊 **Score Tracking** — Tracks performance across all questions
- 📋 **Detailed Performance Report** — Final report with strengths, weaknesses, and study recommendations
- 🔄 **No Repeated Questions** — Memory system ensures fresh questions every time

## Tech Stack

- **LangGraph** — Multi-node agent orchestration with conditional logic and loops
- **RAG (Retrieval Augmented Generation)** — ChromaDB + HuggingFace embeddings
- **Groq LLM API** — Fast, free LLM inference (Llama 3.3 70B)
- **Python** — Core development
- **PyPDF / python-docx** — Document parsing

## How It Works
Upload CV + Job Description
↓
Resume Analyzer Node — extracts skills & identifies gaps
↓
RAG Retriever Node — searches relevant context
↓
Interview Loop Node — generates question → evaluates answer → gives hint or praise
↓
[Loops 5 times]
↓
Report Generator Node — creates final performance report
## Architecture

The system uses a **graph-based agent architecture** with:
- 4 specialized nodes (Resume Analyzer, RAG Retriever, Interview Loop, Report Generator)
- Conditional edges for adaptive flow control
- Loop-back pattern for multi-question interviews
- Persistent state tracking score, questions asked, and feedback

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Groq API key
4. Run the notebook or Streamlit app
5. Upload your CV and target job description
6. Start your mock interview!

## Results

Successfully conducts full 5-question technical interviews with:
- Personalized questions based on real CV/JD content
- Accurate scoring and constructive feedback
- Comprehensive final reports comparing candidate profile to job requirements

## Future Improvements

- [ ] Web deployment via Streamlit
- [ ] Support for behavioral interview questions
- [ ] Multi-language support
- [ ] Voice-based interview simulation
