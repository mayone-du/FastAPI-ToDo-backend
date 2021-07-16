from pathlib import Path
from sys import path

from fastapi import FastAPI
from scripts.initialization import init

from database import Base

# current_dir = Path(__file__).resolve().parent
# path.append(str(current_dir) + '/../')

app = FastAPI()
