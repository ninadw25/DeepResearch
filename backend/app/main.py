from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware # Import the CORS middleware
from fastapi.responses import JSONResponse

from typing import Dict, Any
import asyncio
import time
import uuid

from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langfuse.langchain import CallbackHandler

from app.workflow.graph import research_workflow
from app.models.schemas import *
from app.models.model_config import ModelConfig

from app.utils.config import settings

LANGFUSE_PUBLIC_KEY = settings.LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY = settings.LANGFUSE_SECRET_KEY
LANGFUSE_HOST = settings.LANGFUSE_HOST

langfuse_handler = CallbackHandler()

set_llm_cache(InMemoryCache())
memory = InMemorySaver()

final_results: Dict[str, Any] = {}

app = FastAPI(
    title="Deep Research AI Agent API",
    description="An API for orchestrating an autonomous research agent.",
    version="1.0.0"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


# Binded the checkpointer to the graph at compile time for consistency.
research_graph = research_workflow.compile(checkpointer=memory)

def _resume_and_run_to_completion(task_id: str, resume_value: Any):
    """
    A helper function to resume the graph with a Command and run it to completion.
    """
    config = {
        "configurable": {"thread_id": task_id},
        "callbacks": [langfuse_handler]
    }
    try:
        command = Command(resume=resume_value)
        # Capture the final state returned by the invoke call
        final_state = research_graph.invoke(command, config)
        
        # Store the completed state in our "finish line" dictionary
        final_results[task_id] = final_state
        
        print(f"--- [Task: {task_id}] --- ✅ Completed final run and stored result. ---")
    except Exception as e:
        print(f"Error in resume background task for {task_id}: {e}")
        # Store an error state so the frontend knows something went wrong
        final_results[task_id] = {"error": str(e)}

# --- API Endpoints ---

@app.post("/research", response_model=TaskResponse, status_code=202)
async def start_research(request: ResearchRequest):
    """
    Starts a new research task. This is now a SYNCHRONOUS call.
    The graph will run the planner and then pause immediately, guaranteeing
    the state is saved before this endpoint returns.
    """
    
    task_id = str(uuid.uuid4())
    config = {
        "configurable": {"thread_id": task_id},
        "callbacks": [langfuse_handler] 
    }    
    try:
        model_config = ModelConfig.get_model_config(
            request.model_provider or "groq", 
            request.api_key
        )

        ModelConfig.update_environment(model_config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    initial_state = {
        "original_query": request.query,
        "task_id": task_id,
        "model_provider": request.model_provider or "groq",
        "api_key": request.api_key
    }
    
    try:
        research_graph.invoke(initial_state, config)
    except Exception as e:
        print(f"Error during initial planning for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start research task.")


    return TaskResponse(task_id=task_id)


@app.post("/resume/{task_id}", response_model=StatusResponse)
async def resume_research(
    task_id: str, 
    request: ResumeRequest, 
    background_tasks: BackgroundTasks
):
    """
    Resumes a paused research task with the user-approved research plan.
    """
    resume_value = {
        "research_questions": request.research_questions,
        "task_id": task_id
    }
    background_tasks.add_task(_resume_and_run_to_completion, task_id, resume_value)
    
    return StatusResponse(
        task_id=task_id, 
        status="RESUMED", 
        details="Research is continuing in the background."
    )


@app.get("/status/{task_id}", response_model=GraphStateResponse)
async def get_task_status(task_id: str):
    """
    Retrieves the current state of a research task.
    """
    # First, check if the task is already complete in our final results dict
    if task_id in final_results:
        final_state_values = final_results[task_id]
        return GraphStateResponse(
            status="COMPLETE",
            research_questions=final_state_values.get("research_questions")
        )
    config = {"configurable": {"thread_id": task_id}}
    
    try:
        state_snapshot = research_graph.get_state(config)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")

    current_state_values = state_snapshot.values
    
    if state_snapshot.interrupts:
        status = "AWAITING_INPUT"
        questions = state_snapshot.interrupts[0].value.get("research_questions")
    else:
        status = "RUNNING"
        questions = state_snapshot.values.get("research_questions")
        
    return GraphStateResponse(
        status=status,
        research_questions=questions
    )


@app.get("/results/{task_id}", response_model=FinalReport)
async def get_task_results(task_id: str):
    """
    Retrieves the final report of a completed research task.
    This now looks in our dedicated 'final_results' dictionary.
    """
    # Check if the task is in our "finish line" dictionary
    if task_id not in final_results:
        # If not, the task is either still running or doesn't exist.
        raise HTTPException(status_code=400, detail="Task is not yet complete.")

    final_state_values = final_results[task_id]
    
    if "error" in final_state_values:
        raise HTTPException(status_code=500, detail=f"Task failed: {final_state_values['error']}")

    # --- Logic to assemble the final report (this part is unchanged) ---
    all_sources = []
    for question_sources in final_state_values.get('sources', {}).values():
        all_sources.extend(question_sources)

    unique_citations = []
    seen_sources = set()
    for src in all_sources:
        source_identifier = src.get('source') or src.get('Title')
        if source_identifier and source_identifier not in seen_sources:
            unique_citations.append(Citation(source=source_identifier, content=""))
            seen_sources.add(source_identifier)

    return FinalReport(
        original_query=final_state_values.get("original_query"),
        summary=final_state_values.get('final_report', "Summarization failed."),
        findings=[{"question": q, "results": r}
                  for q, r in (final_state_values.get("findings") or {}).items()],
        citations=unique_citations
    )
