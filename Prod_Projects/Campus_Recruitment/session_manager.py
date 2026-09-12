"""
Hashira ATS - Session Manager
Thread-safe in-memory session manager tracking conversation state, JD, resumes, and results per Telegram user/chat.
"""
import threading
from typing import Dict, Optional, List
from models import UserSession, SessionState, JDAnalysis, UploadedResume, CandidateResult

class SessionManager:
    def __init__(self):
        self._sessions: Dict[int, UserSession] = {}
        self._lock = threading.Lock()

    def get_session(self, chat_id: int) -> UserSession:
        """Get or initialize session for a given chat_id."""
        with self._lock:
            if chat_id not in self._sessions:
                self._sessions[chat_id] = UserSession(chat_id=chat_id)
            return self._sessions[chat_id]

    def set_state(self, chat_id: int, state: SessionState) -> None:
        """Update session state."""
        session = self.get_session(chat_id)
        with self._lock:
            session.state = state

    def set_jd(self, chat_id: int, jd: JDAnalysis, raw_text: str, filename: str = "Job_Description.txt") -> None:
        """Store job description in session."""
        session = self.get_session(chat_id)
        with self._lock:
            session.current_jd = jd
            session.jd_raw_text = raw_text
            session.jd_filename = filename
            session.state = SessionState.WAITING_FOR_RESUMES

    def add_resume(self, chat_id: int, resume: UploadedResume) -> int:
        """Add an uploaded resume and return current resume count."""
        session = self.get_session(chat_id)
        with self._lock:
            session.resumes.append(resume)
            session.state = SessionState.RESUMES_RECEIVED
            return len(session.resumes)

    def set_analysis_results(self, chat_id: int, results: List[CandidateResult]) -> None:
        """Store analysis results in session."""
        session = self.get_session(chat_id)
        with self._lock:
            session.analysis_results = results
            session.state = SessionState.ANALYSIS_COMPLETE
            session.conversation_history.clear()

    def add_conversation_turn(self, chat_id: int, role: str, text: str) -> None:
        """Append to conversational Q&A history."""
        session = self.get_session(chat_id)
        with self._lock:
            session.conversation_history.append({"role": role, "content": text})
            # Keep last 12 turns to stay within token limits
            if len(session.conversation_history) > 12:
                session.conversation_history = session.conversation_history[-12:]

    def reset_session(self, chat_id: int) -> None:
        """Reset user session to fresh state."""
        with self._lock:
            if chat_id in self._sessions:
                self._sessions[chat_id].reset()

session_manager = SessionManager()
