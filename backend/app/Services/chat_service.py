from app.Jarvis.runtime import jarvis


def chat(
    session_id: str,
    message: str,
) -> str:

    return jarvis.chat(
        session_id=session_id,
        message=message,
    )
