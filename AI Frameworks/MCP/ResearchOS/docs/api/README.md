# ResearchOS REST & SSE API Reference

Base URL: `http://localhost:8000`  
Interactive OpenAPI / Swagger UI: `http://localhost:8000/docs`

## Endpoints

### 1. Health Check
- **Route**: `GET /health`
- **Description**: Returns system status, free-tier connector health, and database connection.

### 2. Create Research Run
- **Route**: `POST /api/v1/research`
- **Request Body**:
  ```json
  {
    "query": "Compare LangGraph, CrewAI and Microsoft Agent Framework in 2026",
    "mode": "deep",
    "max_sources": 20
  }
  ```
- **Response**: Full `ResearchRunResponse` containing the generated Markdown report, comparative evaluation matrix, 4-tier verified citations, and complete trace timing.

### 3. Retrieve Research Run
- **Route**: `GET /api/v1/research/{run_id}`
- **Description**: Retrieve run data, report, and trace.

### 4. List All Research Runs
- **Route**: `GET /api/v1/research`
- **Description**: Returns summary list of all recent research runs.

### 5. Evaluate Research Run
- **Route**: `POST /api/v1/research/{run_id}/evaluate`
- **Description**: Executes empirical Ragas-style verification scorecard.

### 6. Standalone Source Search
- **Route**: `GET /api/v1/sources/search?query=LangGraph`
- **Description**: Direct query against arXiv, OpenAlex, and Web without report synthesis.
