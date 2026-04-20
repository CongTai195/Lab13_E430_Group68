from __future__ import annotations

import os
from typing import Any

try:
    import langfuse
    from langfuse import observe
    
    class LangfuseContextWrapper:
        def update_current_trace(self, **kwargs: Any) -> None:
            # For manual updates in v3.2.1, we use the client directly
            # safely checking for method existence to avoid AttributeError
            try:
                client = langfuse.get_client()
                if hasattr(client, "update_current_trace"):
                    client.update_current_trace(**kwargs)
            except Exception:
                pass

        def update_current_observation(self, **kwargs: Any) -> None:
            try:
                client = langfuse.get_client()
                if hasattr(client, "update_current_observation"):
                    client.update_current_observation(**kwargs)
            except Exception:
                pass
            
        def score_current_trace(self, **kwargs: Any) -> None:
            try:
                client = langfuse.get_client()
                if hasattr(client, "score_current_trace"):
                    client.score_current_trace(**kwargs)
            except Exception:
                pass
            
        def flush(self) -> None:
            try:
                client = langfuse.get_client()
                if hasattr(client, "flush"):
                    client.flush()
            except Exception:
                pass

    langfuse_context = LangfuseContextWrapper()
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None: return None
        def update_current_observation(self, **kwargs: Any) -> None: return None
        def score_current_trace(self, **kwargs: Any) -> None: return None
        def flush(self) -> None: return None
    
    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    # Explicitly check for keys to report status accurately
    has_keys = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
    # Also check if we are using the real langfuse or the dummy one
    try:
        import langfuse
        is_real = hasattr(langfuse, "observe")
        return has_keys and is_real
    except ImportError:
        return False
