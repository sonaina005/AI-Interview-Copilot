import streamlit as st
import os
import io
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.messages import HumanMessage

from docx import Document
from pypdf import PdfReader

# Page config
st.set_page_config(page_title="AI Interview Copilot", page_icon="🎯")
st.title("🎯 AI Technical Interview Copilot")

# Get Groq API key
groq_api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")

if not groq_api_key:
    st.warning("⚠️ Please enter your Groq API key in the sidebar to continue")
    st.info("Get a free key at console.groq.com")
    st.stop()

# Setup LLM
llm = ChatGroq(api_key=groq_api_key, model="llama-3.3-70b-versatile")

# File reading function
def read_file(file_content, filename):
    if filename.endswith(".txt"):
        return file_content.decode("utf-8")
    elif filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_content))
        return "".join([page.extract_text() for page in reader.pages])
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(file_content))
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

# State definition
class InterviewState(TypedDict):
    cv_text: str
    jd_text: str
    extracted_skills: str
    retrieved_context: str
    current_question: str
    user_answer: str
    score: int
    feedback: str
    question_count: int
    total_score: int
    asked_questions: list
    final_report: str
    messages: Annotated[list, add_messages]

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "upload"
if "state" not in st.session_state:
    st.session_state.state = {}
if "retriever" not in st.session_state:
    st.session_state.retriever = None

# STAGE 1 - Upload files
if st.session_state.stage == "upload":
    st.header("📄 Upload Your Documents")
    
    cv_file = st.file_uploader("Upload your CV", type=["pdf", "docx", "txt"])
    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])
    
    if cv_file and jd_file:
        if st.button("🚀 Start Interview Preparation"):
            with st.spinner("Analyzing documents and setting up RAG..."):
                cv_text = read_file(cv_file.read(), cv_file.name)
                jd_text = read_file(jd_file.read(), jd_file.name)
                
                # Setup RAG
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                cv_chunks = text_splitter.create_documents([cv_text], metadatas=[{"source": "cv"}])
                jd_chunks = text_splitter.create_documents([jd_text], metadatas=[{"source": "jd"}])
                all_chunks = cv_chunks + jd_chunks
                
                embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
                vectorstore = Chroma.from_documents(documents=all_chunks, embedding=embeddings)
                st.session_state.retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
                
                # Analyze resume
                prompt = f"""Analyze this CV and Job Description:
                CV: {cv_text}
                JD: {jd_text}
                Extract: 1. Key skills from CV 2. Job requirements 3. Skill gaps"""
                
                skills = llm.invoke(prompt).content
                
                st.session_state.state = {
                    "cv_text": cv_text,
                    "jd_text": jd_text,
                    "extracted_skills": skills,
                    "question_count": 0,
                    "total_score": 0,
                    "asked_questions": [],
                }
                st.session_state.stage = "interview"
                st.rerun()

# STAGE 2 - Interview
elif st.session_state.stage == "interview":
    state = st.session_state.state
    
    st.header(f"🎯 Question {state['question_count'] + 1} of 5")
    
    if "current_question" not in state or state.get("need_new_question", True):
        with st.spinner("Generating question..."):
            query = f"Interview questions for: {state['extracted_skills']}"
            docs = st.session_state.retriever.invoke(query)
            context = "\n\n".join([d.page_content for d in docs])
            
            q_prompt = f"""Based on context: {context}
            Skills: {state['extracted_skills']}
            Already asked: {state['asked_questions']}
            Generate ONE new technical interview question. Only the question."""
            
            question = llm.invoke(q_prompt).content
            state["current_question"] = question
            state["need_new_question"] = False
            st.session_state.state = state
    
    st.write(f"**{state['current_question']}**")
    
    answer = st.text_area("Your answer:", key=f"answer_{state['question_count']}")
    
    if st.button("Submit Answer"):
        with st.spinner("Evaluating..."):
            eval_prompt = f"""Question: {state['current_question']}
            Answer: {answer}
            Job requirements: {state['jd_text']}
            Reply EXACTLY: SCORE: [1-10]\nFEEDBACK: [feedback]"""
            
            evaluation = llm.invoke(eval_prompt).content
            
            score = 0
            feedback = ""
            for line in evaluation.split("\n"):
                if "SCORE:" in line:
                    score = int(''.join(filter(str.isdigit, line.split("SCORE:")[1])))
                if "FEEDBACK:" in line:
                    feedback = line.split("FEEDBACK:")[1].strip()
            
            if score >= 6:
                st.success(f"✅ Score: {score}/10")
                st.write(feedback)
            else:
                st.warning(f"💡 Score: {score}/10")
                hint_prompt = f"Question: {state['current_question']}\nGive a helpful hint, don't reveal answer."
                hint = llm.invoke(hint_prompt).content
                st.write(f"**Hint:** {hint}")
            
            state["question_count"] += 1
            state["total_score"] += score
            state["asked_questions"].append(state["current_question"])
            state["need_new_question"] = True
            st.session_state.state = state
            
            if state["question_count"] >= 5:
                st.session_state.stage = "report"
            
            st.rerun()

# STAGE 3 - Final Report
elif st.session_state.stage == "report":
    state = st.session_state.state
    st.header("📊 Final Interview Report")
    
    with st.spinner("Generating your report..."):
        report_prompt = f"""Generate interview performance report:
        Skills: {state['extracted_skills']}
        Total Score: {state['total_score']}/{state['question_count']*10}
        Questions: {state['asked_questions']}
        Job Requirements: {state['jd_text']}
        Include: 1. Overall score 2. Strong areas 3. Weak areas 4. Study topics 5. Recommendation"""
        
        report = llm.invoke(report_prompt).content
        st.markdown(report)
    
    if st.button("🔄 Start New Interview"):
        st.session_state.stage = "upload"
        st.session_state.state = {}
        st.rerun()
