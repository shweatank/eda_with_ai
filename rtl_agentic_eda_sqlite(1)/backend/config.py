import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent/'.env')
OLLAMA_BASE_URL=os.getenv('OLLAMA_BASE_URL','http://localhost:11434')
PLANNER_MODEL=os.getenv('PLANNER_MODEL','gemma4:26b')
CODER_MODEL=os.getenv('CODER_MODEL','qwen2.5-coder:7b')
REVIEWER_MODEL=os.getenv('REVIEWER_MODEL','llama3.1:latest')
MOCK_EDA=os.getenv('MOCK_EDA','true').lower()=='true'
MAX_RETRIES=int(os.getenv('MAX_RETRIES','3'))
WORKSPACE_ROOT=Path(os.getenv('WORKSPACE_ROOT','./runs'))
