from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode 
from langgraph.types import interrupt

import json
from app.schemas import GraphState
from app.agents import planner_agent, tool_router, summarizer_agent, decision_agent
from app.tools import available_tools
import re

import opik
from opik.integrations.langchain import OpikTracer

# opik.configure(use_local=True)
opik_tracer = OpikTracer()

# A helper function to print the state at each step
def print_state(state: GraphState):
    print("--- CURRENT STATE ---")
    print(f"Query: {state['original_query']}")
    print(f"Questions: {state['research_questions']}")
    print(f"Findings: {state.get('findings', {})}")
    print("--------------------")

# Define the nodes of our graph
def planner_node(state: GraphState) -> GraphState:
    """
    Generates the initial research plan.
    """
    print(f"--- [Task: {state['task_id']}] --- 🧠 RUNNING PLANNER ---")
    state['current_task_status'] = "PLANNING: Generating research questions..."
    plan = planner_agent.invoke({"query": state["original_query"]})
    state["research_questions"] = plan.questions
    
    # Initialize findings and sources for each question
    state["findings"] = {q: [] for q in plan.questions}
    state["sources"] = {q: [] for q in plan.questions}
    
    print_state(state)
    return state

def human_approval_node(state: GraphState):
    """
    Pauses the graph to wait for human approval.
    The user can review and edit the research questions.
    """
    print(f"--- [Task: {state['task_id']}] --- ✋ PAUSING FOR HUMAN APPROVAL ---")

    # The interrupt() function pauses execution and surfaces the value to the user.
    # The user's input when resuming will be the return value of this function.
    approved_questions = interrupt(
        {
            "research_questions": state["research_questions"]
        }
    )

    # When the graph is resumed, the approved_questions will be the new,
    # potentially edited, list of questions. We update the state with it.
    return {"research_questions": approved_questions}

def researcher_node(state: GraphState) -> GraphState:
    """
    For each research question, route to the best tool and execute it.
    This node now handles Document objects and separates content from sources.
    """
    print(f"--- [Task: {state['task_id']}] --- 🔍 RUNNING RESEARCHER (with Citation Handling) ---")
    questions = state["research_questions"]
    tool_map = {tool.name: tool for tool in available_tools}

    for i, question in enumerate(questions):
        print(f"--- ❓ RESEARCHING QUESTION: {question} ---")
        state['current_task_status'] = f"EXECUTING: Researching question {i+1}/{len(questions)}..."
        
        tool_name = tool_router.invoke({"question": question}).strip()
        print(f"--- 🛠️ Selected Tool: {tool_name} ---")

        if tool_name in tool_map:
            tool_to_call = tool_map[tool_name]
            # The tool now returns a list of Document objects
            documents = tool_to_call.invoke({"query": question})
            
            # For each document, add content to findings and metadata to sources
            for doc in documents:
                state["findings"][question].append(doc.page_content)
                state["sources"][question].append(doc.metadata)
        else:
            state["findings"][question].append(f"Error: Tool '{tool_name}' not found.")

    print("--- ✅ ALL RESEARCH COMPLETE ---")
    return state

def critique_node(state:GraphState) -> GraphState:
    """
    Decide if the current information is sufficient and we can conclude the research or more research is needed.
    """
    print(f"--- [Task: {state['task_id']}] --- Eval and RUNNING Decider ---")
    
    # Create a formatted string of all findings and their sources
    context = ""
    for i, (question, findings) in enumerate(state['findings'].items()):
        context += f"Research Question {i+1}: {question}\n\n"
        for j, finding in enumerate(findings):
            source_info = state['sources'][question][j]
            # Use a generic source identifier. A simple URL or title.
            source = source_info.get('source') or source_info.get('Title')
            context += f"Finding: {finding}\nSource: {source}\n\n"
        context += "---\n\n"
    
    decision_str = decision_agent.invoke({
        "context": context,
        "question": state["original_query"]
    })
    
    # Use regex to find the keyword reliably
    match = re.search(r'\b(conclude|insufficient)\b', decision_str, re.IGNORECASE)
    
    decision = "insufficient" # Default to this for safety
    if match:
        decision = match.group(1).lower()
        
    print(f"--- 🤔 CRITIQUE DECISION: {decision.upper()} ---")
    state["decision"] = decision # Store the clean string 'conclude' or 'insufficient'
    return state
    

def summarize_node(state: GraphState) -> GraphState:
    """
    Synthesizes the findings into a final report.
    """
    print(f"--- [Task: {state['task_id']}] --- ✍️ RUNNING SUMMARIZER ---")
    state['current_task_status'] = "SUMMARIZING: Compiling final report with citations..."

    # Create a formatted string of all findings and their sources
    context = ""
    for i, (question, findings) in enumerate(state['findings'].items()):
        context += f"Research Question {i+1}: {question}\n\n"
        for j, finding in enumerate(findings):
            source_info = state['sources'][question][j]
            # Use a generic source identifier. A simple URL or title.
            source = source_info.get('source') or source_info.get('Title')
            context += f"Finding: {finding}\nSource: {source}\n\n"
        context += "---\n\n"

    report = summarizer_agent.invoke({
        "context": context,
        "query": state["original_query"]
    })
    state["final_report"] = report.content
    return state

def decide_next_step(state: GraphState):
    if state['decision'] == 'conclude':
        return "summarizer"
    else:
        # Default to researching again if critique is "insufficient" or any other unexpected value
        return "researcher"

# Define the graph workflow
workflow = StateGraph(GraphState)

# Add the nodes
workflow.add_node("planner", planner_node)
workflow.add_node("human_approval", human_approval_node) #<-- New
workflow.add_node("researcher", researcher_node)
# workflow.add_node("critique", critique_node)
workflow.add_node("summarizer", summarize_node)

# Set the entry point
workflow.set_entry_point("planner")

#Edges connecting the nodes
workflow.add_edge("planner", "human_approval")
workflow.add_edge("human_approval", "researcher") 
workflow.add_edge("researcher", "summarizer")

# workflow.add_edge("researcher", "critique")
# workflow.add_conditional_edges(
#     "critique",
#     decide_next_step,
#     {"summarizer": "summarizer", "researcher": "researcher"}
# )
workflow.add_edge("summarizer", END)

# Compile the graph into a runnable app
# research_workflow = workflow.compile()
research_workflow = workflow
# opik_tracer = OpikTracer(graph=research_workflow.get_graph(xray=True))

# opik_tracer.flush()