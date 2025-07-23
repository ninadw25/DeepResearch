from langchain.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_community.document_loaders import WikipediaLoader, ArxivLoader
from langchain_tavily import TavilySearch
from langchain_core.documents import Document # Import the Document class
from typing import List

import json
from app.config import settings

# --- Instantiate Tavily Tool ---
# We keep this instance for its searching capability
tavily_search_instance = TavilySearch(
    max_results=3,
    tavily_api_key=settings.TAVILY_API_KEY
)
# --- This is the corrected web_search tool ---
# @tool
# def web_search(query: str) -> List[Document]:
#     """
#     Performs a web search using Tavily.
#     Use this for current events, opinions, or general questions.
#     Returns a list of documents with content and source metadata.
#     """
#     try:
#         # 1. Instantiate the tool, explicitly passing the API key
#         tavily_tool = TavilySearch(
#             max_results=3,
#             tavily_api_key=settings.TAVILY_API_KEY
#         )

#         # 2. Invoke the tool, which returns a Python dictionary
#         dict_result = tavily_tool.invoke({"query": query})
        
#         # 3. Directly access the list of results from the 'results' key
#         #    (No more json.loads() needed)
#         results_list = dict_result.get("results", [])
        
#         # 4. Handle the case where the search finds nothing
#         if not results_list:
#             return [Document(page_content="No results were found for this search query.")]

#         # 5. Convert the dictionary results into standard Document objects
#         return [
#             Document(
#                 page_content=res.get("content", ""),
#                 metadata={"source": res.get("url", "N/A")}
#             )
#             for res in results_list
#         ]
#     except Exception as e:
#         print(f"Error in Tavily search: {e}")
#         return [Document(page_content=f"An error occurred during web search: {e}")]

# In app/tools.py

@tool
def web_search(query: str) -> List[Document]:
    """
    Performs a web search using Tavily.
    This is an instrumented version for deep debugging.
    """
    print("\n--- ENTERING web_search TOOL ---")
    try:
        print("1. Initializing TavilySearch...")
        tavily_tool = TavilySearch(
            max_results=3,
            tavily_api_key=settings.TAVILY_API_KEY
        )
        print(f"2. TavilySearch initialized. Invoking with query: '{query}'")
        dict_result = tavily_tool.invoke({"query": query})
        
        print("3. Invoke successful. Raw result received.")
        # To avoid printing huge results, we'll just print the type and keys
        print(f"   - Type of result: {type(dict_result)}")
        if isinstance(dict_result, dict):
            print(f"   - Keys found: {dict_result.keys()}")

        results_list = dict_result.get("results", [])
        
        print(f"4. Extracted {len(results_list)} articles from the 'results' key.")
        if not results_list:
            print("5. No results found. Returning 'No results' document.")
            return [Document(page_content="No results were found for this search query.")]

        print("6. Processing results into Document objects.")
        documents = [
            Document(
                page_content=res.get("content", ""),
                metadata={"source": res.get("url", "N/A")}
            )
            for res in results_list
        ]
        print("7. Finished processing. Returning documents.")
        return documents

    except Exception as e:
        # This will now catch any error that occurs and print a full traceback
        print(f"\n--- FATAL ERROR in web_search: {e} ---\n")
        import traceback
        traceback.print_exc()
        return [Document(page_content=f"An error occurred during web search: {e}")]

@tool
def arxiv_search(query: str) -> List[Document]:
    """
    Searches the ArXiv repository for academic papers.
    Returns a list of documents with summaries and source metadata.
    """
    try:
        loader = ArxivLoader(query=query, load_max_docs=2)
        documents = loader.get_summaries_as_docs()
        # The loader already returns Document objects with metadata
        return documents
    except Exception as e:
        return [Document(page_content=f"An error occurred during ArXiv search: {e}")]

@tool
def wikipedia_search(query: str) -> List[Document]:
    """
    Searches Wikipedia for articles.
    Returns a list of documents with content and source metadata.
    """
    try:
        loader = WikipediaLoader(query=query, load_max_docs=1, doc_content_chars_max=4000)
        # The loader already returns Document objects with metadata
        return loader.load()
    except Exception as e:
        return [Document(page_content=f"An error occurred during Wikipedia search: {e}")]

# --- Update Tool Lists ---
available_tools = [web_search, arxiv_search, wikipedia_search]
# Note: We are no longer directly using the tavily_tool instance in the list, 
# but our custom web_search tool which uses it.
converted_tools = [convert_to_openai_tool(t) for t in available_tools]