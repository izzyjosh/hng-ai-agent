# Project Description
This is a FastAPI + Pydantic-ai project of a Grammatical error corrector that returns the correcfed sentence with explanation

---

## Project Features
- Grammatical error correction
- Proper input validation with **Pydantic**
- AI agent implementation using **pydantic-ai**
- a2a-protocol implementation
- Gemini AI model used

---

## Tech Stack
- **FastAPI**: for exposing a2a-protocol endpoint
- **Pydantic**: for schema validation(input and output)
- **Pydanti-ai**: For implementation of LLM
- **uvicorn**: for exposing ASGI app

---

## Setup Instructions
Follow this steps to get the project running

### Clone Respository
```bash
git clone https://github.com/izzyjosh/hng-ai-agent.git
cd hng-ai-agent
```

### Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Setting up .env file
Set up the following environment variables
```
GOOGLE_API_KEY=pass_your_api_key_here
PORT=5000
```
### Run project
```bash
python main.py
```
---

## Testing
- make a post request to /a2a/grammar-check
- The body should be in this format
```
{
    "jsonrpc": "2.0",
    "id": "test-001",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "what is we name?"
          }
        ],
        "messageId": "msg-001",
        "taskId": "task-001"
      },
      "configuration": {
        "blocking": true
      }
    }
  }'
```
- All you have to do next is to witness the chefing.

---

## Grammar Agent Docs
As stated above, the agent helps to correct Grammatical error in user input

### endpoint
This project exposes a single endpoint for a2a-protocol interaction. The endpoint receives a post request togther with a body in the format shown above.

From the a2a body, it extract the user message and pass it to the agent for processing, via a function called `run ` in the GrammarAgent class

### Agent
The agent was built using pydantic-AI which implement Gemini LLM. To get this working, you need to get a gemini api key and set it in the environment variable

### Request & Response
The request and response are filtered and validated using pydantic which is a great feature of pydantic AI. 

---

## Thank You for reading from my little work.
