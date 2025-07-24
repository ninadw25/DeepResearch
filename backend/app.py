import streamlit as st
import requests
import time
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Deep Research AI Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Backend Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- Helper Functions ---
def start_research_task(query):
    """Sends a request to start a new research task."""
    try:
        response = requests.post(f"{BACKEND_URL}/research", json={"query": query})
        response.raise_for_status()
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
        if e.response and e.response.status_code == 404:
            return {"status": "PENDING", "details": "Task initializing..."}
        st.warning(f"Could not retrieve task status: {e}")
        return None

def resume_task(task_id, research_questions):
    """Sends the approved/edited plan to the backend to resume the task."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/resume/{task_id}",
            json={"research_questions": research_questions}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error resuming task: {e}")
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
st.sidebar.title("🔬 Agent Configuration")
st.sidebar.info(
    "This application demonstrates a multi-agent AI system that can be supervised by a human. "
    "After generating a plan, the agent will pause and await your approval before executing the research."
)

st.title("Deep Research AI Agent")
st.markdown("Enter your research query below to begin. The agent will generate a plan for your approval.")

# --- Session State Management ---
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'task_status' not in st.session_state:
    st.session_state.task_status = None
if 'research_questions' not in st.session_state:
    st.session_state.research_questions = []
if 'final_report' not in st.session_state:
    st.session_state.final_report = None

# --- Main Application Flow ---

# 1. Input Form to Start Research
if not st.session_state.task_id:
    with st.form("research_form"):
        query = st.text_area("Enter your research query:", height=150)
        submitted = st.form_submit_button("🔬 Generate Research Plan")
        if submitted and query:
            with st.spinner("Agent is thinking... Contacting the Planner Agent."):
                task_info = start_research_task(query)
                if task_info:
                    st.session_state.task_id = task_info.get("task_id")
                    st.success("Task started! Polling for research plan...")
                    st.rerun()

# 2. Polling and HITL Approval Form
if st.session_state.task_id and st.session_state.task_status != "COMPLETE":
    with st.spinner("Polling for agent status..."):
        status_data = get_task_status(st.session_state.task_id)
        if status_data:
            st.session_state.task_status = status_data.get("status")
            st.session_state.research_questions = status_data.get("research_questions", [])

    # If agent is waiting for input, show the approval form
    if st.session_state.task_status == "AWAITING_INPUT" and st.session_state.research_questions:
        st.info("✅ **Human-in-the-Loop:** The agent has created a plan and is waiting for your approval.")
        
        with st.form("approval_form"):
            st.subheader("📝 Proposed Research Plan")
            st.markdown("You can edit the research questions below before approving.")
            
            # Display questions in editable text areas
            edited_questions = []
            for i, q in enumerate(st.session_state.research_questions):
                edited_q = st.text_area(f"Question {i+1}", value=q, height=100)
                edited_questions.append(edited_q)

            approve_button = st.form_submit_button("🚀 Approve and Resume Research")

            if approve_button:
                with st.spinner("Sending approved plan to agent..."):
                    resume_response = resume_task(st.session_state.task_id, edited_questions)
                    if resume_response and resume_response.get("status") == "RESUMED":
                        st.success("Agent has resumed research in the background!")
                        st.session_state.task_status = "RESUMED"
                        st.rerun()

    # If agent is running after approval, show progress
    elif st.session_state.task_status == "RESUMED":
        st.warning("⏳ **Research in Progress:** The agent is now executing the approved plan. This may take a moment. The page will automatically update when the final report is ready.")
        time.sleep(5) # Wait before re-checking status
        st.rerun()

    # If the task is somehow complete, move to the final report stage
    elif st.session_state.task_status == "COMPLETE":
        st.rerun()
    
    else:
        # Initial state before the plan is ready
        st.info("Waiting for the agent to generate the research plan...")
        time.sleep(3)
        st.rerun()


# 3. Display Final Report
if st.session_state.task_status == "COMPLETE":
    if not st.session_state.final_report:
        with st.spinner("Fetching final report..."):
            st.session_state.final_report = get_task_results(st.session_state.task_id)

    if st.session_state.final_report:
        st.balloons()
        st.header("📄 Final Research Report")
        report_data = st.session_state.final_report
        st.markdown(report_data.get("summary", "No summary available."))
        
        with st.expander("📜 **Citations & Sources**"):
            citations = report_data.get("citations", [])
            if citations:
                for i, citation in enumerate(citations):
                    st.markdown(f"{i+1}. [{citation.get('source')}]({citation.get('source')})")
            else:
                st.markdown("No citations were generated for this report.")
        
        # Add a button to start a new research task
        if st.button("Start New Research"):
            st.session_state.task_id = None
            st.session_state.task_status = None
            st.session_state.research_questions = []
            st.session_state.final_report = None
            st.rerun()

