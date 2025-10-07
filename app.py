import streamlit as st
import requests
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the BACKEND_URL from the environment variables
BACKEND_URL = os.getenv("BACKEND_URL")


st.set_page_config(layout="wide")
st.title("Multi-Agentic System with Dynamic Decision Making")

# Initialize session state
if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = None

with st.sidebar:
    st.header("📄 Upload a PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        if st.button("Upload and Process PDF"):
            with st.spinner("Uploading and processing..."):
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                try:
                    response = requests.post(f"{BACKEND_URL}/upload_pdf/", files=files)
                    response.raise_for_status()
                    
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.success(f"✅ Successfully processed `{uploaded_file.name}`")
                    # Use st.rerun() to immediately show the clear button after upload
                    st.rerun()

                except requests.exceptions.HTTPError as err:
                    st.error("An HTTP error occurred on the server.")
                    st.code(f"Status Code: {err.response.status_code}\nResponse Text:\n{err.response.text}", language="text")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection failed. Is the FastAPI backend running? Details: {e}")

    # Displays the current PDF and adds a button to clear it
    if st.session_state.uploaded_filename:
        st.info(f"Current PDF in context: **{st.session_state.uploaded_filename}**")
        if st.button("Clear PDF Context"):
            st.session_state.uploaded_filename = None
            st.rerun()  # Reruns the script to update the UI

# Main chat interface
query = st.text_input("Ask your question:", placeholder="e.g., What are the latest developments in AI?")

if st.button("Submit Query"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Thinking... The agents are at work! 🤔"):
            payload = {
                "query": query,
                "filename": st.session_state.uploaded_filename
            }
            try:
                response = requests.post(f"{BACKEND_URL}/ask/", data=payload)
                if response.status_code == 200:
                    result = response.json()
                    
                    st.subheader("Final Answer")
                    st.markdown(result['final_answer'])
                    
                    with st.expander("🤖 Agent Decision & Traceability"):
                        st.markdown("**Controller's Reasoning:**")
                        st.info(result['controller_decision']['reasoning'])
                        
                        st.markdown("**Agents Called:**")
                        st.code(", ".join(result['controller_decision']['agents']), language='bash')
                        
                        st.markdown("**Retrieved Documents:**")
                        st.json(result['retrieved_docs'])
                else:
                    st.error(f"Error from backend: {response.json().get('detail')}")
            except requests.exceptions.ConnectionError:
                st.error("Connection failed. Is the FastAPI backend running?")
