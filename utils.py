import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
synthesis_model = genai.GenerativeModel('gemini-2.5-flash') 

def synthesize_answer(query: str, context: str):
    """Uses an LLM to generate a final answer from the collected context."""
    if not context.strip():
        context = "No information was found by the agents. Please rely on your general knowledge."

    prompt = f"""
    You are a helpful AI assistant. Your task is to provide a clear and concise answer to the user's query based *only* on the provided context.
    If the context is insufficient, state that you could not find enough information.

    User Query: {query}

    Context from Agents:
    {context}

    Answer:
    """
    try:
        response = synthesis_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in synthesis: {e}")
        return "Sorry, I encountered an error while generating the final answer."