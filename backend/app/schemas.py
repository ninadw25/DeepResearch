from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, TypedDict

# === API Schemas (for FastAPI input/output) ===

class ResearchRequest(BaseModel):
    """Request model for starting a new research task."""
    query: str = Field(..., description="The user's research query.")
    # In the future, you could add more fields like 'depth', 'preferred_sources', etc.

class TaskResponse(BaseModel):
    """Response model for acknowledging a task has started."""
    task_id: str = Field(..., description="The unique ID for the research task.")

class StatusResponse(BaseModel):
    """Response model for polling the status of a task."""
    task_id: str
    status: str = Field(..., description="Current status, e.g., 'PENDING', 'PLANNING', 'EXECUTING', 'COMPLETE', 'FAILED'.")
    details: Optional[str] = None # Optional message, e.g., "Generated 5 research questions."

class GraphStateResponse(BaseModel):
    status: str
    research_questions: Optional[List[str]] = None

class Citation(BaseModel):
    """Model for a single citation."""
    source: str = Field(..., description="The URL or identifier of the source.")
    content: str = Field(..., description="The relevant snippet from the source.")

class FinalReport(BaseModel):
    """The final structured report returned to the user."""
    original_query: str
    summary: str = Field(..., description="A high-level summary of the research findings.")
    findings: List[Dict[str, Any]] = Field(..., description="A list of detailed findings, possibly structured by sub-topic.")
    citations: List[Citation]

class ResumeRequest(BaseModel):
    """take the list of research questions sent by the user and update the agent's saved "memory" for that specific task."""
    research_questions : List[str]


# === Internal State Schema (for LangGraph) ===

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    This dictionary is passed between all nodes in the graph.
    """
    original_query: str
    research_questions: List[str]
    
    # Each key in findings is a research_question
    findings: Dict[str, List[str]]
    
    # Each key in sources is a research_question, value is a list of citations
    sources: Dict[str, List[Dict[str, str]]]
    
    # Current step/status message for the user
    decision : str
    current_task_status: str
    final_report: str
    task_id : str
    