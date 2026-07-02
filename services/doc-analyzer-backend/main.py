import uvicorn

from config.service_config import service_config

if __name__ == "__main__":
    uvicorn.run(
        "api.api:app",
        host=service_config.host,
        port=service_config.port,
        timeout_keep_alive=service_config.timeout_keep_alive,
        timeout_graceful_shutdown=service_config.timeout_graceful_shutdown,
        reload=service_config.reload,
    )
