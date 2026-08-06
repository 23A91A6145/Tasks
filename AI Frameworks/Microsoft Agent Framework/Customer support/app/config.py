import os
from dotenv import load_dotenv
from agent_framework.ollama import OllamaChatClient
from agent_framework.openai import OpenAIChatClient

load_dotenv()

# LLM Config
class RuntimeConfig:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    
    # Ollama settings
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Groq settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    
    # Gemini settings (via OpenAI compatibility layer)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

# Folders configuration
WORKSPACE_DIR = "/home/cherry/Desktop/1_Gen/Tasks/MAF/Customer support"
HISTORY_DIR = os.path.join(WORKSPACE_DIR, "history")
LOGS_DIR = os.path.join(WORKSPACE_DIR, "logs")
CHECKPOINTS_DIR = os.path.join(WORKSPACE_DIR, "history", "checkpoints")

# Ensure directories exist
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CHECKPOINTS_DIR, exist_ok=True)

# Allowed types for secure checkpoint unpickling (FileCheckpointStorage)
ALLOWED_CHECKPOINT_TYPES = [
    # Python Core types
    "types:GenericAlias",
    
    # Handoff structures
    "agent_framework_orchestrations._handoff:HandoffAgentUserRequest",
    
    # Ollama SDK types
    "ollama._types:Message",
    "ollama._types:Message.ToolCall",
    "ollama._types:Message.ToolCall.Function",
    "ollama._types:ChatResponse",
    
    # OpenAI / Groq / Gemini SDK types
    "openai.types.chat.chat_completion_message:ChatCompletionMessage",
    "openai.types.chat.chat_completion_message_tool_call:ChatCompletionMessageToolCall",
    "openai.types.chat.chat_completion_message_tool_call:Function",
    "openai.types.chat.chat_completion:ChatCompletion",
    "openai.types.chat.chat_completion:Choice",
    "openai.types.chat.chat_completion_chunk:ChoiceDeltaToolCall",
    "openai.types.chat.chat_completion_chunk:ChoiceDeltaToolCallFunction",
    
    # Agent Framework types
    "agent_framework._types:Message",
    "agent_framework._types:TextContent",
    "agent_framework._types:FunctionCallContent",
    "agent_framework._types:FunctionResultContent",
    "agent_framework._types:AgentResponse",
    "agent_framework._types:AgentResponseUpdate",
    "agent_framework._types:OptionsCoT",
    "agent_framework._types:CompactionState",
    "agent_framework._types:Context",
]

class PatchedOllamaChatClient(OllamaChatClient):
    """Subclass of OllamaChatClient that strips unsupported parameters and forces temperature=0.0."""
    def _prepare_options(self, messages, options):
        run_options = super()._prepare_options(messages, options)
        run_options.pop("allow_multiple_tool_calls", None)
        
        # Inject options nested dictionary for maximum determinism and stable function calling
        if "options" not in run_options or run_options["options"] is None:
            run_options["options"] = {}
            
        run_options["options"]["temperature"] = 0.0
        run_options["options"]["top_p"] = 0.9
        
        return run_options

def get_chat_client():
    """Returns the chat client configured in the environment."""
    provider = RuntimeConfig.LLM_PROVIDER.strip().lower()
    if provider == "ollama":
        return PatchedOllamaChatClient(model=RuntimeConfig.OLLAMA_MODEL, host=RuntimeConfig.OLLAMA_HOST)
    elif provider == "openai":
        return OpenAIChatClient(model=RuntimeConfig.OPENAI_MODEL, api_key=RuntimeConfig.OPENAI_API_KEY, base_url=RuntimeConfig.OPENAI_BASE_URL)
    elif provider == "groq":
        return OpenAIChatClient(model=RuntimeConfig.GROQ_MODEL, api_key=RuntimeConfig.GROQ_API_KEY, base_url=RuntimeConfig.GROQ_BASE_URL)
    elif provider == "gemini":
        return OpenAIChatClient(model=RuntimeConfig.GEMINI_MODEL, api_key=RuntimeConfig.GEMINI_API_KEY, base_url=RuntimeConfig.GEMINI_BASE_URL)
    else:
        # Default fallback to local Ollama
        return PatchedOllamaChatClient(model="llama3.2:3b", host="http://localhost:11434")
