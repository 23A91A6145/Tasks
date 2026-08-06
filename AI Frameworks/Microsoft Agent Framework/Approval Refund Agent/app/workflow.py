import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import CHECKPOINT_DIR
from app.utils import logger

class WorkflowState:
    """
    Manages workflow checkpointing. Paused agent states can be persisted to disk
    and reloaded to resume the task flow once human approval is obtained.
    """
    
    @staticmethod
    def save_checkpoint(request_id: str, state_data: Dict[str, Any]) -> bool:
        """Saves agent execution state to a JSON checkpoint file."""
        try:
            filepath = CHECKPOINT_DIR / f"{request_id}.json"
            with open(filepath, "w") as f:
                json.dump(state_data, f, indent=4)
            logger.info(f"💾 Checkpoint saved: {request_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save checkpoint {request_id}: {e}")
            return False

    @staticmethod
    def load_checkpoint(request_id: str) -> Optional[Dict[str, Any]]:
        """Loads agent execution state from a JSON checkpoint file."""
        filepath = CHECKPOINT_DIR / f"{request_id}.json"
        if not filepath.exists():
            logger.warning(f"⚠️ Checkpoint not found: {request_id}")
            return None
        try:
            with open(filepath, "r") as f:
                state_data = json.load(f)
            logger.info(f"🔌 Checkpoint loaded: {request_id}")
            return state_data
        except Exception as e:
            logger.error(f"Failed to load checkpoint {request_id}: {e}")
            return None

    @staticmethod
    def delete_checkpoint(request_id: str) -> bool:
        """Removes the checkpoint file once a workflow is finalized."""
        filepath = CHECKPOINT_DIR / f"{request_id}.json"
        if filepath.exists():
            try:
                filepath.unlink()
                logger.info(f"🧹 Checkpoint deleted: {request_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete checkpoint {request_id}: {e}")
        return False
