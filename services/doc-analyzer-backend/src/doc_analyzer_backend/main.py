import uvicorn

from src.doc_analyzer_backend.config.loader.settings import app_settings

if __name__ == "__main__":
    service_config = app_settings().service
    uvicorn.run(
        "api.api:app",
        host=service_config.host,
        port=service_config.port,
        timeout_keep_alive=service_config.timeout_keep_alive,
        timeout_graceful_shutdown=service_config.timeout_graceful_shutdown,
        reload=service_config.reload,
    )
