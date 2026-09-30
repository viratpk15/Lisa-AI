from app.Jarvis.runtime import jarvis


def chat(
    session_id: str,
    message: str,
    user_name: str | None = None,
) -> str:

    return jarvis.chat(
        session_id=session_id,
        message=message,
        user_name=user_name,
    )
