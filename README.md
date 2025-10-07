
# Multi-Agentic System with Dynamic Decision Making

This project implements a Multi-Agent AI System that dynamically decides which specialized agents to use for answering user queries. The system includes a FastAPI backend, and integrates Google AI Studio (Gemini) APIs for intelligent orchestration and answer synthesis.

───────────────────────────────────────────────────────────────────────
# 🏛️ System Architecture

At its heart, the system is a web application with a clear separation of duties:

### 🖥️ Frontend (Streamlit)
This is the user interface where you type your questions and upload files.  
It’s the public-facing part of the application that allows you to:
- Enter text queries
- Upload PDFs
- View results, agent usage, and decision rationale

### ⚙️ Backend (FastAPI)
This is the engine room of the system.  
It runs on a server and manages:
- The core logic and orchestration
- Communication between agents
- Integration with the LLM and APIs
- Logging of controller decisions and traces

## 🧩 Core Components

### 1. 🧠 Controller Agent (The "Manager")
The Controller Agent is the most critical part of the system.  
When you ask a question, the Controller is the first component to process it.

**Responsibilities:**
- Analyze the user query
- Decide which specialized agent(s) to call
- Use an LLM (Gemini) to reason and route dynamically
- Log all decisions, rationales, and agent calls

The Controller ensures that every query is handled by the most appropriate agent.

### 2. 🤖 Specialized Agents (The "Team Members")
These agents are domain experts that perform the actual work after the Controller assigns them a task.

#### 🧾 PDF RAG Agent
- Expert at reading and understanding documents
- Activated when a user uploads a PDF
- Extracts, embeds, and retrieves relevant information
- Provides summaries or answers derived from document content

#### 🌐 Web Search Agent
- Acts as a real-time researcher
- Handles queries about current events, latest developments, or news
- Uses APIs like SerpAPI or DuckDuckGo to fetch up-to-date information

#### 📚 ArXiv Agent
- Functions as an academic specialist
- Fetches recent research papers, scientific studies, and technical papers
- Utilizes the ArXiv API or Hugging Face’s arxiv_dataset

---

### 3. 🧩 Synthesizer
After all specialist agents have gathered their information (the context), the data is passed to the Synthesizer — a final LLM component.

*here context means all the history of human ,ai and tool messages.

**Responsibilities:**
- Review and combine all gathered information
- Generate a single, coherent, and well-structured answer
- Ensure readability and consistency before presenting the response to the user

───────────────────────────────────────────────────────────────────────
## 🔄 The Workflow

The journey from your question to the final answer follows a well-orchestrated sequence:

1. **Query**  
   You type a question in the Streamlit frontend.

2. **Routing**  
   The FastAPI backend receives the query and passes it to the Controller Agent.  
   The Controller analyzes the query and decides which agent(s) to call.  
   Example:  
   > “This is a research question — call the ArXiv Agent.”  
   The reasoning and routing decision are logged for traceability.

3. **Execution**  
   The backend calls the chosen specialist agent(s), which gather the required information from their sources (PDFs, web, or ArXiv).

4. **Synthesis**  
   The information from the agents is compiled into a unified context document and given to the Synthesizer, which produces the final answer.

5. **Response**  
   The Synthesizer writes the final answer, which is sent back to the frontend for you to read.

───────────────────────────────────────────────────────────────────────
## 🚀 Getting Started

Follow these steps to set up and run the multi-agent system on your local machine.

# Step 1: Clone the Repository
First, clone the project repository from GitHub to your local computer.

```
git clone https://github.com/gauravbondegit/multi_agent_system.git

cd <your-repository-directory>
```
# Step 2: Set Up a Virtual Environment

Create a virtual environment
```
python -m venv myenv
```
Activate the virtual environment
```
myenv\Scripts\activate
```
# Step 3: Install Dependencies

```
pip install -r requirements.txt
```
# Step 4: Configure Environment Variables
The application requires a Google API key to function.

1. Create the file named .env in the project's root directory.

2. Open the file and write-
```
# .env file
GOOGLE_API_KEY="AIzaSy...your...actual...key..."
BACKEND_URL="http://127.0.0.1:8000"
```
__Step 5: Run the Application__
**__Step 5: Run the Application__**
_Step 5: Run the Application_

This application has two parts: a backend server and a frontend interface. You need to run them in two separate terminals.

1. Run the Backend Server (Terminal 1):
- Make sure your virtual environment is activated.
- Start the FastAPI server using Uvicorn.
```
uvicorn main:app --reload
```
- You should see a message indicating the server is running on http://127.0.0.1:8000. Leave this terminal running.

2. Run the Frontend App (Terminal 2):

- Open a new terminal and activate the virtual environment there as well.

- Start the Streamlit application.
```
streamlit run app.py
```
- This will automatically open a new tab in your web browser with the application's user interface.

You can now interact with your multi-agent AI system.



───────────────────────────────────────────────────────────────────────


───────────────────────────────────────────────────────────────────────



