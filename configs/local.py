from os import getenv

# this configuration has default values set
local_config = {
    "config": "local",
    "host": getenv("HOST", "0.0.0.0"),
    "port": int(getenv("PORT", "8000")),
    "postgres_connection_string": getenv("POSTGRES_CONNECTION_STRING", "postgresql+asyncpg://localhost:5432/sys"),
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    "llm_api_key": getenv("LLM_API_KEY"),
    "llm_base_url": getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
    "llm_model": getenv("LLM_MODEL", "gemini-2.5-flash"),
}