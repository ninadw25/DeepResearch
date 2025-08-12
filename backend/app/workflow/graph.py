from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from app.models.schemas import GraphState
from app.workflow.agents import planner_agent, tool_router, summarizer_agent
from app.utils.tools import available_tools

# --- Helper function for logging ---
def print_state(state: GraphState):
    print("--- CURRENT STATE ---")
    print(f"Query: {state['original_query']}")
    print(f"Questions: {state['research_questions']}")
    # Only print findings if they exist and are not empty
    if findings := state.get('findings'):
        if any(findings.values()):
            print(f"Findings: {state.get('findings', {})}")
    print("--------------------")

# --- Node Definitions ---

def planner_node(state: GraphState) -> GraphState:
    """
    Generates the initial research plan.
    """
    task_id = state.get('task_id', 'UNKNOWN')
    print(f"--- [Task: {task_id}] --- 🧠 RUNNING PLANNER ---")
    
    plan = planner_agent.invoke({"query": state["original_query"]})
    
    # Initialize findings and sources for the generated questions
    state["research_questions"] = plan.questions
    state["findings"] = {q: [] for q in plan.questions}
    state["sources"] = {q: [] for q in plan.questions}
    
    print_state(state)
    return state

def human_approval_node(state: GraphState):
    """
    Pauses the graph to wait for human approval.
    The user can review and edit the research questions.
    """
    task_id = state['task_id']
    print(f"--- [Task: {task_id}] --- ✋ PAUSING FOR HUMAN APPROVAL ---")
    
    resume_data = interrupt({"research_questions": state["research_questions"]})
    
    return {
        "research_questions": resume_data["research_questions"],
        "task_id": resume_data["task_id"]
    }

def researcher_node(state: GraphState) -> GraphState:
    """
    For each research question, route to the best tool and execute it.
    """
    task_id = state.get('task_id', 'UNKNOWN')
    print(f"--- [Task: {task_id}] --- 🔍 RUNNING RESEARCHER ---")
    
    questions = state["research_questions"]
    tool_map = {tool.name: tool for tool in available_tools}
    
    if "findings" not in state:
        state["findings"] = {}
    if "sources" not in state:
        state["sources"] = {}
        
    for q in questions:
        state["findings"].setdefault(q, [])
        state["sources"].setdefault(q, [])

    for question in questions:
        # Skip questions that already have findings
        if state["findings"][question]:
            print(f"--- ❓ SKIPPING QUESTION (already researched): {question} ---")
            continue

        print(f"--- ❓ RESEARCHING QUESTION: {question} ---")
        tool_name = tool_router.invoke({"question": question}).strip()
        print(f"--- 🛠️ Selected Tool: {tool_name} ---")

        if tool_name in tool_map:
            tool_to_call = tool_map[tool_name]
            documents = tool_to_call.invoke({"query": question})
            for doc in documents:
                state["findings"][question].append(doc.page_content)
                state["sources"][question].append(doc.metadata)
        else:
            state["findings"][question].append(f"Error: Tool '{tool_name}' not found.")

    print("--- ✅ ALL RESEARCH COMPLETE ---")
    return state

def summarize_node(state: GraphState) -> GraphState:
    """
    Synthesizes the findings and sources into a final report.
    This is an instrumented version for deep debugging.
    """
    task_id = state.get('task_id', 'UNKNOWN')
    print(f"--- [Task: {task_id}] --- ✍️ RUNNING SUMMARIZER ---")

    try:
        print("1. Building context for summarizer...")
        context = ""
        for i, (question, findings) in enumerate(state['findings'].items()):
            context += f"Research Question {i+1}: {question}\n\n"
            for j, finding in enumerate(findings):
                # Ensure source_info exists and is not out of bounds
                if j < len(state['sources'][question]):
                    source_info = state['sources'][question][j]
                    source = source_info.get('source') or source_info.get('Title')
                    context += f"Finding: {finding}\nSource: {source}\n\n"
                else:
                    context += f"Finding: {finding}\nSource: Not available\n\n"
            context += "---\n\n"
        
        print(f"2. Context built. Total length: {len(context)} characters.")
        print("3. Invoking summarizer agent...")

        report = summarizer_agent.invoke({
            "context": context,
            "query": state["original_query"]
        })
        
        print("4. Summarizer agent finished successfully.")
        state["final_report"] = report.content
        return state

    except Exception as e:
        print(f"\n---  FATAL ERROR in summarize_node: {e} ---\n")
        import traceback
        traceback.print_exc()
        # Set a clear error message in the final report
        state["final_report"] = "Error during summarization. The research material may have been too long for the language model to process."
        return state


workflow = StateGraph(GraphState)

workflow.add_node("planner", planner_node)
workflow.add_node("human_approval", human_approval_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("summarizer", summarize_node)

workflow.set_entry_point("planner")

workflow.add_edge("planner", "human_approval")
workflow.add_edge("human_approval", "researcher")
workflow.add_edge("researcher", "summarizer")
workflow.add_edge("summarizer", END)

# research_workflow = workflow.compile()
research_workflow = workflow
