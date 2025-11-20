
# DB Discovery AI Integration

## Authentication
- Basic Authentication with membership username and password

## Authorization
- All endpoints secured with role based system for each endpoint check authenticate_and_authorize middleware
- permission example api.create_membership -- api.create_database

## Security
- All credentials for membership databases secured with rsa encryption


## 🚀 Getting Started

### Prerequisites

- Python 3.13  
- PostgreSQL database  
- LLM API key
- (Optional) Docker for containerized setup  

### Local installation

1. Clone the repository:
   * git clone https://github.com/emirhanayhan/db_discovery_ai_integration.git
   * cd db_discovery_ai_integration

2. Create and Activate Virtual Environment

   * python -m venv venv
   * source venv/bin/activate

3. Install Requirements
   * pip install -r requirements.txt

4. Create RSA Private Key For Encryption
   * in app directory import and run src.security.encryption generate_private_key

4. Run FastAPI
   * python main.py --config=local --migrate=true


### Environment Variables
     ENV  --> DEFAULT(only in local config)
   * HOST --> 0.0.0.0
   * PORT --> 8000
   * POSTGRES_CONNECTION_STRING --> postgresql+asyncpg://localhost:5432/sys
   * WORKER_COUNT --> 1
   * LLM_API_KEY --> No default
   * LLM_BASE_URL --> https://generativelanguage.googleapis.com/v1beta/openai/
   * LLM_MODEL --> gemini-2.5-flash


### ENDPOINTS
  * /api/v1/healthcheck GET
  * /api/v1/memberships POST
  * /api/v1/membership-dbs POST
  * /api/v1/membership-dbs/{db_id}/extract POST
  * /api/v1/membership-dbs/metadata GET
  * /api/v1/membership-dbs/metadata/{metadata_id} GET
  * /api/v1/membership-dbs/metadata/{metadata_id} DELETE
  * /api/v1/membership-dbs/{metadata_id}/classify/{column_id} POST
