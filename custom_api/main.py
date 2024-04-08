
import os
from fastapi import FastAPI
from fastapi import APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.module_api import router as module_router
from starlette.middleware.base import BaseHTTPMiddleware



app = FastAPI()

router = APIRouter()
router.include_router(module_router)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

