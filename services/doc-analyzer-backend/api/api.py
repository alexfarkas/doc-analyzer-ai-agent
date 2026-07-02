import logging
from contextlib import asynccontextmanager

from db_repository import PromptRepository
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag_client import ChromaDBClientFactory

from agent.agent import Agent
from agent.council.council import Council
from api.config.logger_setup import setup_logging
from api.routers.data_sources_router import router as data_sources_router
from api.routers.doc_analysis_router import router as doc_analysis_router
from api.routers.system_router import router as system_router
from config.db_config import db_config
from config.llm_config import llm_config
from config.logger_config import logger_config
from config.rag_config import rag_config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(
        log_path=logger_config.path,
        log_level=logger_config.level,
        write_to_file=logger_config.write_to_file,
    )

    logger.info("Starting app...")

    prompt_repository = None
    if db_config.use_db_prompts:
        logger.info("Initializing DB prompts repository...")
        prompt_repository = PromptRepository(db_config.url)
        logger.info("DB prompts repository initialized")
    else:
        logger.info("Using local prompts")

    chromadb_client_factory = None
    if rag_config.use_vector_db:
        logger.info("Initializing ChromaDB client factory for RAG...")
        chromadb_client_factory = ChromaDBClientFactory(rag_config)
        logger.info("ChromaDB client factory for RAG initialized")
    else:
        logger.info("No RAG is used")

    logger.info("Agent initialization")
    app.state.agent = await Agent.create_agent(
        llm_config, prompt_repository, chromadb_client_factory
    )
    logger.info("Agent initialized")

    logger.info("Council initialization")
    app.state.council = await Council.init_council(
        prompt_repository, chromadb_client_factory
    )
    logger.info("Council initialized")

    logger.info("App is started")

    yield

    logger.info("Stopping app, resources cleanup")
    app.state.agent = None
    app.state.council = None


app = FastAPI(
    title="Doc Analyser AI Agent",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(system_router, tags=["System"])
app.include_router(doc_analysis_router, tags=["Doc Analysis"])
app.include_router(data_sources_router, tags=["Data Sources"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def disable_compression(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/doc/chat/stream"):
        response.headers["Content-Encoding"] = "identity"
    return response


import api.exceptions.exception_handlers  # noqa: E402, F401
