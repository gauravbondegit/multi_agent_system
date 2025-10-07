from langchain_community.tools import ArxivQueryRun

def query_arxiv_agent(query: str):
    """Queries ArXiv for papers and returns a summary."""
    try:
        arxiv_tool = ArxivQueryRun()
        # Clean query for ArXiv
        clean_query = query.replace("latest papers on", "").replace("arxiv", "").strip()
        results = arxiv_tool.run(clean_query)
        return results, {"source": "ArXiv Search"}
    except Exception as e:
        print(f"ArXiv search failed: {e}")
        return "Could not perform ArXiv search.", {"error": str(e)}
    

