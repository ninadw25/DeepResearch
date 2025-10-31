# DeepResearch: A Stateful, Multi-Agent AI Research System

DeepResearch is an advanced, multi-agent AI system designed to conduct complex, in-depth research. Unlike stateless chatbots, this agent operates on a stateful, graph-based architecture, allowing it to plan, execute multi-step research, and synthesize comprehensive, cited reports with live human supervision.

**Watch a live demo of the agent in action:** 

Uploading DeepResearch Agents.mp4…

## Technical Architecture & Core Features

This is not a simple script; it is a complete, full-stack application engineered for robustness and professional-grade observability.

### 1. Multi-Agent Collaborative Workflow

The system's "brain" is built with **LangGraph**. It operates as a stateful graph that orchestrates a team of specialized AI agents:

* **Planner Agent:** Acts as the project manager. It receives a complex user query and breaks it down into a logical, step-by-step research plan.
* **Researcher Agent:** An intelligent worker that executes the plan. It uses a **Tool Router** to select the right tool for each question, gathering data from web search (Tavily) or academic archives (ArXiv).
* **Summarizer Agent:** The expert analyst. It receives all the raw findings and synthesizes them into a single, cohesive, and fully-cited final report.

### 2. Human-in-the-Loop (HITL) Supervision

This is the agent's most powerful feature. The workflow is architected to explicitly **pause** after the planning stage by calling a `dynamic interrupt`. This allows the user to act as a supervisor, reviewing, editing, and approving the agent's research plan before execution begins. This ensures the agent's work is always aligned with the user's goals.

### 3. Long-Term Memory (Mem0 Integration)

The agent learns and evolves. It is integrated with **Mem0.ai** as a managed, cloud-based memory layer.

* **Memory-Informed Planning:** Before planning, the agent searches its memory for relevant past research to avoid redundant work and create more intelligent, focused plans.
* **Memory-Augmented Synthesis:** The final report is synthesized from *both* new findings and relevant past memories, allowing the agent to demonstrate accumulated knowledge.

### 4. Full-Stack & Containerized Architecture

The entire application is a decoupled, multi-service system:

* **Backend:** A robust and asynchronous **FastAPI** server that manages all agentic logic and API endpoints.
* **Frontend:** A dynamic, responsive user interface built in **React.js**.
* **Deployment:** The entire application (backend, frontend, and memory services) is fully containerized with **Docker** and orchestrated with **Docker Compose**, making it portable and ready for any cloud environment.

### 5. End-to-End Observability

The agent's "mind" is not a black box. The entire workflow, from the initial plan to the final summary, is tracked using **Langfuse**. This allows for deep, step-by-step tracing of the agent's reasoning, tool calls, and performance, which was critical for debugging and optimizing its behavior.

## Architectural Flow

This diagram illustrates the flow of information and control between the user and the agent's core components.

<img width="1024" height="768" alt="DeepResearch" src="https://github.com/user-attachments/assets/33afce83-d43c-407a-92ee-761abe4e81be" />

## Technical Stack Deep Dive

While the features above describe *what* the agent does, this section explains *how* the technology components work together.

* **FastAPI (Backend API):** Serves as the central nervous system. It's not just a simple data API; it **manages the agent's lifecycle**. It exposes HTTP endpoints (`/research`, `/status`, `/resume`) that allow the React frontend to start, check on, and send feedback to the agent. It holds the `InMemorySaver` (the checkpointer) and is responsible for invoking the LangGraph graph, either synchronously for planning or in the background for research.

* **LangGraph (The Agent's "Brain"):** This is the core of the backend's logic. It's a **state machine** that defines the agent's thought process as a graph of nodes.
    * **Nodes:** Each agent (Planner, Researcher, etc.) is a node.
    * **Edges:** These define the paths the agent can take.
    * **`interrupt()`:** The `human_approval_node` uses this function to explicitly pause the entire graph and wait for external input.
    * **`Command(resume=...)`:** The agent resumes execution only when it receives this command from our `/resume` endpoint, which passes in the user-approved plan.

* **React.js (The Interactive UI):** The frontend is a stateful application that intelligently handles the agent's asynchronous nature.
    * It uses `useState` to manage the application's current `stage` (e.g., `start`, `approval`, `results`).
    * It uses `useEffect` hooks to implement a **robust polling strategy**. After resuming the agent, the `ReportDisplay` component repeatedly polls the `/results` endpoint, patiently waiting for the long-running background task to complete before rendering the final report.

* **Langfuse (LLMOps & Observability):** This is our "flight recorder" for the agent's mind.
    * **Integration:** The `CallbackHandler` is passed into the `config` of every `research_graph.invoke()` call.
    * **Key Feature:** It automatically uses the `thread_id` (which we map to our `task_id`) to **stitch together separate, disjointed API calls** (`/research` and `/resume`) into a single, unified trace. This was critical for debugging the agent's stateful behavior across the human-in-the-loop pause.

<img width="1901" height="936" alt="image" src="https://github.com/user-attachments/assets/939e0d8e-2652-47be-99d5-661c3ee3a979" />

Check the tracing from this link: https://cloud.langfuse.com/project/cmeaa5gq500szad0721mg0801/traces/016bb1aad24bd010f9392865daa1d9b1?timestamp=2025-09-16T19:18:54.785Z

* **Docker & Docker Compose (The "Shipping Container"):**
    * **`Dockerfile` (Backend):** A standard Python container that runs our FastAPI server using `uvicorn`.
    * **`Dockerfile` (Frontend):** A professional, **multi-stage build**. It uses a Node.js "builder" container to compile the React app, then copies the final, optimized static files into a tiny, secure **Nginx** container for serving.
    * **`docker-compose.yml`:** The master blueprint that builds and runs all services, creates a private network for them to communicate, and manages our persistent memory volume.
```eof
