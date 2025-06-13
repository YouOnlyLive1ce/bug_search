from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.faiss_pipeline import faiss_search
from contextlib import asynccontextmanager

# Define FastAPI app
app = FastAPI()

# Input schema for queries
class Query(BaseModel):
    code: str

class Answer(BaseModel):
    code: str

databases={}

@asynccontextmanager
async def lifespan(app: FastAPI):        
    databases['faiss'] = faiss_search
    yield
    # after app closed: Clean up the database and release the resources
    databases.clear()

app = FastAPI(lifespan=lifespan)

@app.post("/retrieve", response_model=Answer)
async def predict(data: Query):
    try:
        result = databases['faiss'](data)
        return Answer(code=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
