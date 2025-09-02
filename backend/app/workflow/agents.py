from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama 
from langchain_openai import ChatOpenAI  

from pydantic import BaseModel, Field
from typing import List, Literal

import json

from app.utils.config import settings
from app.utils.tools import converted_tools

import re

# --- LLM Initialization ---
llm = None 

if settings.LLM_PROVIDER == "groq":
    print("🚀 Using Groq as the LLM provider.")
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama3-8b-8192", 
        temperature=0
    )
elif settings.LLM_PROVIDER == "google":
    if not settings.GOOGLE_API_KEY:
        raise ValueError("LLM_PROVIDER is set to 'google' but GOOGLE_API_KEY is missing.")
    print("✨ Using Google Gemini as the LLM provider.")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0
    )
elif settings.LLM_PROVIDER == "openrouter":
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("LLM_PROVIDER is set to 'openrouter' but OPENROUTER_API_KEY is missing.")
    print("🌐 Using OpenRouter as the LLM provider.")
    llm = ChatOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model="anthropic/claude-3.5-sonnet",  # You can change this to your preferred model
        temperature=0
    )
elif settings.LLM_PROVIDER == "ollama":
    print("🗿 Using local Ollama as the LLM provider.")
    llm = ChatOllama(model="gemma3:4b", temperature=0)
else:
    raise ValueError(f"Unsupported LLM provider: '{settings.LLM_PROVIDER}'. Please choose 'groq', 'google', 'openrouter', or 'ollama'.")


class ResearchPlan(BaseModel):
    """
    The plan of research questions to answer the user's query.
    """
    questions: List[str] = Field(description="A list of 3 to 5 specific questions to research.")
    
class RouteQuery(BaseModel):
    """
    Specifies the tool to use for a given research question.
    """
    tool_name: str = Field(..., description="The name of the tool to use (e.g., 'arxiv_search', 'wikipedia_search').")
    
class DecisionResult(BaseModel): choice: Literal['CONCLUDE', 'INSUFFICIENT']
    
planner_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         "You are an expert research planner. Your goal is to create a step-by-step research plan "
         "to answer the user's query. Generate a list of 3 to 6 specific, answerable questions that, "
         "when combined, will provide a comprehensive answer."
         "\n\nIMPORTANT: You should ONLY generate questions. Do NOT use any tools or functions. "
         "Just create a structured list of research questions."
         "You have also been provided with a list of relevant memories from past research. Use these memories to create a more focused and advanced research plan. "
         "Do not generate questions that are already answered in the provided memories. Instead, focus on questions that will uncover new information or go deeper into the topic.\n\n"
         "--- RELEVANT MEMORIES ---\n"
         "{memories}\n"
         "--- END MEMORIES ---"        ),
        ("user", "Based on the provided memories, create a research plan for the following query: {query}")
    ]
)

router_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are an expert at routing a user's question to the best data source.\n"
         "You must choose from the following tools. Respond with ONLY the tool name.\n\n"
         "== TOOLS ==\n"
         "1. `web_search`: Use for questions about current events, product information, specifications, prices, user reviews, or general topics that require accessing the live internet.\n"
         "2. `wikipedia_search`: Use for questions about well-established historical facts, definitions, or general knowledge about people, places, and concepts.\n"
         "3. `arxiv_search`: ONLY use for questions about scientific papers, deep technical concepts, machine learning algorithms, or physics research.\n\n"
         "== EXAMPLES ==\n"
         "Question: 'What are the specs of the new ASUS ROG laptop?'\n"
         "Tool: web_search\n\n"
         "Question: 'Who was the first emperor of Rome?'\n"
         "Tool: wikipedia_search\n\n"
         "Question: 'What are recent papers on transformer model optimization?'\n"
         "Tool: arxiv_search\n\n"
         "Question: 'What are user reviews for the Dell XPS 15?'\n"
         "Tool: web_search"
        ),
        ("user", "Question: {question}\nTool:")
    ]
)

# decider_prompt = ChatPromptTemplate.from_messages(
#     [
#         # explicitly tell the agent to proceed when and run research again in what conditions.
#         ("system",
#          " You need to look at the given information which will be used to answer the users query and determine if the current amount of research is sufficient or not\n"
#          "you need to understand the user query and for the query this is the current research content found. \n"
#          "--- BEGIN RESEARCH MATERIAL ---\n"
#          "{context}"
#          "--- END RESEARCH MATERIAL ---"
#          """Now these are the metrics by which you will decide if we need to do more research or we can conclude the research and forward with the current information
#             When to Research Further:         
#             1. Additional research is performed when:
#             2. Important parts of the topic are still unanswered.
#             3. Information conflicts and needs to be resolved through more sources.
#             4. Only a narrow or single perspective has been found, and diverse views are needed.
#             5. The available data lacks authority or clarity, requiring more reputable references.
            
#             When to Conclude
#             Research stops when:
#             1. Evidence is sufficient, well-supported, and robust.
#             2. Information is confirmed across several independent sources.
#             3. New findings are repetitive or add little additional value.
#             4. The report covers the user’s query as completely and clearly as possible.
            
#             IMPORTANT RULE: If a finding for a question contains the text 'No results were found' or 'An error occurred', you MUST choose 'CONCLUDE'. Do not ask to research again if a tool has already failed for that specific topic, as this will cause an infinite loop. Concluding allows the agent to move on to the next question.
#          """
#          ),
#         ("user", "The original query was: '{query}'. Now, based on the query give me output strictly in the words 'CONCLUDE' if there is noo need to do more research and the current findings are enough OR output 'INSUFFICIENT' if the current findings are lacking and more research needs to be done. respond with ONLY ONE of the following words: CONCLUDE or INSUFFICIENT")
#     ]
# )

decider_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a pragmatic project manager. Your only job is to decide if the research findings are 'good enough' to write a helpful summary for the user. The goal is not a perfect, exhaustive report.\n\n"
         "1. If the findings contain concrete facts, names, numbers, or relevant information that can answer the user's query, you MUST respond with the single word: **CONCLUDE**\n\n"
         "2. If the findings are empty, contain only errors (like 'No results found'), or are completely irrelevant, you MUST respond with the single word: **INSUFFICIENT**\n\n"
         "Do not explain your reasoning. Respond with only one word."
        ),
        ("user",
         "Original Query: '{question}'\n\n"
         "--- RESEARCH FINDINGS ---\n"
         "{context}\n"
         "--- END FINDINGS ---\n\n"
         "Decision (CONCLUDE or INSUFFICIENT):"
         )
    ]
)
summarizer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are an expert research analyst. Your goal is to synthesize research findings into a comprehensive report.\n"
         "You have been given a user's query, and a collection of research findings organized by sub-question.\n"
         "Please write a detailed, well-structured report that directly answers the user's query.\n"
         "IMPORTANT: For each piece of information you use, you MUST cite the source using markdown footnotes. For example: 'This is a fact from a source.[^1]'.\n"
         "At the end of the report, you MUST include a 'Citations' section that lists all the sources used, formatted clearly.\n\n"
         "Here is the research material you must use:\n"
         "--- BEGIN RESEARCH MATERIAL ---\n"
         "{context}"
         "--- END RESEARCH MATERIAL ---"
         "In addition to the research material You have also been given a user's query, a list of RELEVANT MEMORIES from past research, and a list of NEW FINDINGS from recent research.\n"
         "At the end of the report, include a 'Citations' section. The RELEVANT MEMORIES do not need to be cited.\n\n"
         "--- RELEVANT MEMORIES ---\n"
         "{memories}\n"
        ),
        ("user", "My original query was: '{query}'. Now, please generate the full report based on the provided research material and previous memories.")
    ]
)

planner_agent = planner_prompt | llm.with_structured_output(ResearchPlan)

if settings.LLM_PROVIDER != "ollama":    
    tool_router = (
        router_prompt
        | llm.bind(tools=converted_tools, tool_choice="none")  # <-- The critical new instruction
        | StrOutputParser()
    )
else:
    tool_router = router_prompt | llm | StrOutputParser()

if settings.LLM_PROVIDER != "ollama":    
    decision_agent = (
        decider_prompt
        | llm.bind(tools=converted_tools, tool_choice="none")  # <-- The critical new instruction
        | StrOutputParser()
    )
else:
    decision_agent = decider_prompt | llm | StrOutputParser()

summarizer_agent = summarizer_prompt | llm

