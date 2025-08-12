import os
import json
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

# my sample code to check the tavilyapi 

def run_diagnostic():
    """
    A simple function to test the TavilySearch tool directly.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("ERROR: TAVILY_API_KEY not found in your .env file!")
        return

    print("--- Initializing TavilySearch tool ---")
    tavily_tool = TavilySearch(tavily_api_key=api_key)

    test_query = "What are the best gaming laptops under 1 lakh rupees in India?"
    print(f"--- Sending query: '{test_query}' ---")

    try:
        raw_result = tavily_tool.invoke({"query": test_query})

        print("\n\n--- DIAGNOSTIC REPORT ---")
        print(f"1. Type of result: {type(raw_result)}")
        print("\n2. Raw Result Content:")
        print(raw_result)
        print("------------------------")

        if isinstance(raw_result, str):
            print("\n3. Analysis: The result is a STRING.")
            print("   Attempting to parse it as JSON...")
            try:
                parsed_json = json.loads(raw_result)
                print("   SUCCESS: Parsed string as JSON.")
                if isinstance(parsed_json, dict) and 'results' in parsed_json:
                    print(f"   Found {len(parsed_json['results'])} items in the 'results' key.")
                else:
                    print("   NOTE: Parsed JSON is not a dictionary with a 'results' key.")
            except json.JSONDecodeError:
                print("   FAILURE: Could not parse the string as JSON.")

        elif isinstance(raw_result, list):
            print("\n3. Analysis: The result is a LIST.")
            print(f"   The list contains {len(raw_result)} items.")

        elif isinstance(raw_result, dict):
            print("\n3. Analysis: The result is a DICTIONARY.")
            print("   Keys in the dictionary:", raw_result.keys())
            if 'results' in raw_result:
                print(f"   Found {len(raw_result['results'])} items in the 'results' key.")

    except Exception as e:
        print(f"\n\n--- AN ERROR OCCURRED DURING THE TEST ---")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_diagnostic()