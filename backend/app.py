import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

# --- Page Configuration ---
st.set_page_config(
    page_title="Deep Research AI Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Backend Configuration ---
# Make sure your FastAPI backend is running at this address
BACKEND_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def start_research_task(query, provider):
    """Sends a request to the backend to start a new research task."""
    try:
        # Note: The provider choice here is for display. 
        # Ensure your backend is actually running with the selected provider.
        response = requests.post(f"{BACKEND_URL}/research", json={"query": query})
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {e}")
        return None

def get_task_status(task_id):
    """Polls the backend for the status of a research task."""
    try:
        response = requests.get(f"{BACKEND_URL}/status/{task_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Don't show an error for 404, as the task might just not be ready
        if e.response and e.response.status_code == 404:
            return {"status": "PENDING", "details": "Task initializing..."}
        st.warning(f"Could not retrieve task status: {e}")
        return None

def get_task_results(task_id):
    """Gets the final results of a completed research task."""
    try:
        response = requests.get(f"{BACKEND_URL}/results/{task_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching final results: {e}")
        return None

# --- UI Layout ---

# Sidebar for configuration
with st.sidebar:
    st.title("🔬 Agent Configuration")
    st.markdown("Configure the AI agent's settings before starting your research.")
    
    # Provider selection
    # This is a reminder for the user to have the correct backend running.
    provider = st.selectbox(
        "Select LLM Provider",
        ("ollama", "groq", "google"),
        index=0,
        help="Ensure your backend's .env file is configured for this provider before starting."
    )
    st.info(f"**Reminder:** Your backend must be running with the **{provider.upper()}** provider selected.")

    st.markdown("---")
    st.markdown(
        "This application demonstrates a multi-agent AI system that performs deep research on any given topic. "
        "It autonomously plans research questions, gathers information from multiple sources, and synthesizes the findings into a comprehensive report with citations."
    )

# Main content area
st.title("Deep Research AI Agent")
st.markdown("Welcome! Enter your research query below to begin.")

# Initialize session state
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'research_complete' not in st.session_state:
    st.session_state.research_complete = False
if 'final_report' not in st.session_state:
    st.session_state.final_report = None

# Input form for the research query
with st.form("research_form"):
    query = st.text_area(
        "Enter your research query:",
        height=150,
        placeholder="e.g., What is the future of renewable energy, and what are the key challenges and opportunities?"
    )
    submitted = st.form_submit_button("🚀 Start Research")

    if submitted:
        if not query:
            st.warning("Please enter a research query.")
        else:
            # Reset state for new research
            st.session_state.task_id = None
            st.session_state.research_complete = False
            st.session_state.final_report = None
            
            with st.spinner("Contacting the research agent... Please wait."):
                task_info = start_research_task(query, provider)
                if task_info:
                    st.session_state.task_id = task_info.get("task_id")
                    st.success("Research task started successfully!")
                    st.rerun()

# --- Polling and Display Logic ---
if st.session_state.task_id and not st.session_state.research_complete:
    st.info("Research in progress... The agent's findings will appear below in real-time.")
    
    # Placeholders for dynamic content
    status_placeholder = st.empty()
    questions_placeholder = st.empty()
    findings_placeholder = st.empty()

    with st.spinner("The agent is thinking..."):
        while not st.session_state.research_complete:
            status_data = get_task_status(st.session_state.task_id)

            if status_data:
                # Display current status
                status_placeholder.info(f"**Agent Status:** {status_data.get('details', 'Working...')}")
                
                # Display intermediate results if available
                intermediate_results = status_data.get('intermediate_results', {})
                
                if intermediate_results:
                    # Display Research Questions
                    questions = intermediate_results.get('questions')
                    if questions:
                        with questions_placeholder.container():
                            with st.expander("📝 **Research Plan** (Generated by Planner Agent)", expanded=True):
                                for i, q in enumerate(questions):
                                    st.markdown(f"{i+1}. {q}")
                    
                    # Display Findings
                    findings = intermediate_results.get('findings')
                    if findings and any(findings.values()):
                        with findings_placeholder.container():
                             with st.expander("📚 **Live Research Findings** (Gathered by Executor Agents)", expanded=True):
                                for question, results in findings.items():
                                    if results:
                                        st.markdown(f"**> {question}**")
                                        for res in results:
                                            # Truncate long results for cleaner display
                                            if "No results" in res or "Error" in res:
                                                st.warning(f"   - {res}")
                                            else:
                                                st.text(f"   - {res[:250]}...")
                                st.markdown("---")


                # Check for completion
                if status_data.get("status") == "COMPLETE":
                    st.session_state.research_complete = True
                    st.balloons()
                    st.success("Research complete! Fetching the final report...")
                    st.rerun()

                elif status_data.get("status") == "FAILED":
                    st.error("Research task failed. Please check the backend logs.")
                    st.session_state.task_id = None # Reset task
                    break
            
            time.sleep(3) # Wait before polling again

# --- Display Final Report ---
if st.session_state.research_complete:
    if not st.session_state.final_report:
        st.session_state.final_report = get_task_results(st.session_state.task_id)

    if st.session_state.final_report:
        st.markdown("---")
        st.header("📄 Final Research Report")
        
        report_data = st.session_state.final_report
        
        # Display the main summary
        st.markdown(report_data.get("summary", "No summary available."))
        
        # Display citations in an expander
        with st.expander("📜 **Citations & Sources**"):
            citations = report_data.get("citations", [])
            if citations:
                for i, citation in enumerate(citations):
                    st.markdown(f"{i+1}. [{citation.get('source')}]({citation.get('source')})")
            else:
                st.markdown("No citations were generated for this report.")

