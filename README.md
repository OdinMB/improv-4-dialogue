# "AI Improv" project at Berlin conference on 15 October, 2024

Audio bot that extracts knowledge from a semantic database
Using OpenAI Realtime API and some basic RAG (probably FAISS?) via tool calling

Starting point: https://github.com/Chainlit/cookbook/tree/main/realtime-assistant

Test for new laptop environment

## DEPLOYMENT on render

- Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `chainlit run -h --host 0.0.0.0 app.py`
  (`-h` for headless to make sure that no browser window is opened
  `--host` necessary since security update in chainlit 1.1.something)
  `--port ####` is optional