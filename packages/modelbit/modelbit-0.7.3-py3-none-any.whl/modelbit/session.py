from typing import Any, List

_sessions: List[Any] = []

def rememberSession(clientSession: Any):
  _sessions.append(clientSession)

def anyAuthenticatedSession():
  for session in _sessions:
    if session.isAuthenticated():
      return session
  return None
