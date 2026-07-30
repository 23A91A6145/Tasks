# Changelog

## v1.1.0 (2026-07-30)

### Breaking Changes
- History API response format changed: `/history` now returns `{entries, total, limit, offset}` instead of a bare list
- Database schema updated: added `conversation_id` and `feedback` columns (auto-migration for existing DBs)

### New Features
- **Multi-turn conversation** — conversation history passed as context to agents
- **Conversation ID tracking** — group Q&A pairs into threaded conversations
- **Feedback mechanism** — thumbs up/down on responses (API + UI)
- **History search** — search queries and responses by keyword
- **Category filtering** — filter history by billing/technical/sales/escalate
- **Export** — download history as JSON or CSV
- **System statistics endpoint** — `/stats` with counts, averages, feedback breakdown
- **Delete entries** — DELETE `/history/{id}` endpoint
- **Thread-safe HistoryStore** — singleton with write-lock, safe for concurrent API access
- **SQLite schema migration** — automatic ALTER TABLE for existing databases

### Bug Fixes
- Streamlit `processing` flag now actually disables chat input during processing
- `_parse_classification` uses regex word boundaries to avoid false matches
- `_parse_validation` handles edge case of bare "REVISE" with no following text
- Calculator: recursion depth protection prevents stack overflow DoS
- Calculator: empty expression returns proper error message
- History UI shows all tool badges, not just the first one
- `st.rerun()` only called after new messages, not on every render
- New Chat button preserves session state properly
- Raw exception messages no longer leaked to API clients
- Docker compose starts both API and UI services
- `.dockerignore` prevents cache/log files from entering container images
- All `__init__.py` files properly export their package contents

### UI Improvements
- Custom CSS with agent badges, tool badges, validation indicators
- Welcome/onboarding card with example prompts on first visit
- Typing indicator (status message) during processing
- Search bar + category filter + result count in History page
- Export CSV button in History
- Feedback thumbs up/down on responses
- Execution time displayed in chat
- Settings page with bar chart breakdown by category
- Sidebar with conversation count and quick actions
- Dark theme refined (`config.toml`)

### API Improvements
- Pydantic models with field validation (min/max length, value ranges)
- Request IDs for tracing
- Paginated history with `offset`, `total`, `limit`
- Chat accepts `conversation_id` for multi-turn context
- `conversation_id` auto-generated if not provided
- Stats endpoint with feedback breakdown

### Technical Improvements
- Configurable `MAX_REVISIONS`, `MAX_QUERY_LENGTH`, `MAX_HISTORY_LIMIT`, `CALCULATOR_MAX_NESTING` via `.env`
- Duplicate `result.raw` extraction extracted to `_get_result()` helper
- `_parse_classification` uses `re.findall(r'\b\w+\b')` for word boundary matching
- HistoryStore: singleton pattern + write-lock for thread safety
- HistoryStore: `close()` method called on FastAPI shutdown
- Cleaned up dead files (tools/knowledge_base.py, tools/utils.py)

## v1.0.0 (2026-07-30)

### Volume I — AI Support Fundamentals
- Router Agent for query classification
- Billing, Technical, Sales specialist agents
- YAML-driven agent and task configuration
- CLI entry point with single-query and demo modes

### Volume II — Tool Integration
- Web Search tool (DuckDuckGo, free)
- Calculator tool (safe AST evaluation)
- Weather tool (Open-Meteo, free)
- Currency Converter tool (Frankfurter, free)
- Company Data tool (mock local data)
- Agent-tool binding per specialist

### Volume III — Multi-Agent Collaboration
- Validator Agent for response quality review
- 5-point quality checklist
- Revision loop with 1 retry on rejection
- Validation status in all output interfaces

### Volume IV — Professional Platform
- Streamlit web UI with dark theme
- FastAPI REST API
- SQLite conversation history store
- CORS support for cross-origin access

### Volume V — Production & Portfolio
- Comprehensive test suite (57 tests)
- Docker support (Dockerfile + docker-compose)
- Makefile for common commands
- MIT License
- Example queries guide
- Full documentation
