from os import getenv

prod_config = {
    "config": "prod",
    "host": getenv("HOST", "0.0.0.0"),
    "port": int(getenv("PORT", "8000")),
    "postgres_connection_string": getenv("POSTGRES_CONNECTION_STRING"),
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    "llm_api_key": getenv("LLM_API_KEY"),
    "llm_base_url": getenv("LLM_BASE_URL"),
    "llm_model": getenv("LLM_MODEL"),
}