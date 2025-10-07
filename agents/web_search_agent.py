from langchain_community.tools import DuckDuckGoSearchRun

def query_web_search_agent(query: str):
    """Performs a web search and returns a summary."""
    try:
        search = DuckDuckGoSearchRun()
        results = search.run(query)
        return results, {"source": "DuckDuckGo Search"}
    except Exception as e:
        print(f"Web search failed: {e}")
        return "Could not perform web search.", {"error": str(e)}