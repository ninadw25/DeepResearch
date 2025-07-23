from fastapi import FastAPI, BackgroundTasks, HTTPException

from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver

from app.graph import research_workflow
from app.schemas import ResearchRequest, TaskResponse, StatusResponse, FinalReport, Citation

import uuid

# A simple in-memory "database" to track task status.
tasks = {}
set_llm_cache(InMemoryCache())
memory = InMemorySaver()

app = FastAPI(
    title="Deep Research AI Agent API",
    description="An API for orchestrating an autonomous research agent.",
    version="0.1.0"
)

research_graph = research_workflow.with_config(
    checkpointer=memory,
    interrupt_before=["researcher"]
)

# --- Real Research Function ---
def run_research_graph(task_id: str, query: str):
    """Runs the research graph and updates the task status in-memory."""
    tasks[task_id] = {"status": "PENDING", "details": "Task received and queued."}
    
    # The initial state for our graph
    initial_state = {"original_query": query}
    
    # The `stream` method executes the graph and yields the state at each step
    for step in research_graph.stream(initial_state):
        # The key of the dictionary is the name of the node that just ran
        node_name = list(step.keys())[0]
        current_state = step[node_name]
        
        # Update the shared tasks dictionary with the latest status
        tasks[task_id] = {
            "status": current_state.get('current_task_status', 'EXECUTING'),
            "details": f"Completed step: {node_name}",
            "intermediate_results": {
                "questions": current_state.get('research_questions'),
                "findings": current_state.get('findings')
            }
        }
    
    # When the graph is finished, get the final state
    final_state = research_graph.invoke({"original_query": query})
    
    # Flatten the list of all sources from the state
    all_sources = []
    for question_sources in final_state.get('sources', {}).values():
        all_sources.extend(question_sources)

    # Convert to Citation objects, removing duplicates
    unique_citations = []
    seen_sources = set()
    for src in all_sources:
        source_identifier = src.get('source') or src.get('Title')
        if source_identifier and source_identifier not in seen_sources:
            unique_citations.append(
                Citation(source=source_identifier, content="") # We leave content blank for now
            )
            seen_sources.add(source_identifier)

    report = FinalReport(
        original_query=query,
        summary=final_state.get('final_report', "Summarization failed."),
        findings=[{"question": q, "results": r} for q, r in final_state['findings'].items()],
        citations=unique_citations # Populate with our collected citations
    )
    
    tasks[task_id] = {"status": "COMPLETE", "result": report.model_dump()}
    print(f"Task {task_id}: Research complete.")


# --- API Endpoints ---
# (No changes needed to the endpoints themselves)

@app.post("/research", response_model=TaskResponse, status_code=202)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "PENDING", "details": "Task received and queued."}
    
    background_tasks.add_task(run_research_graph, task_id, request.query)

    return TaskResponse(task_id=task_id)


@app.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return StatusResponse(
        task_id=task_id,
        status=task.get("status"),
        details=task.get("details")
    )


@app.get("/results/{task_id}", response_model=FinalReport)
async def get_task_results(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.get("status") != "COMPLETE":
        raise HTTPException(status_code=400, detail=f"Task is not yet complete. Current status: {task.get('status')}")
    return task.get("result")