from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.documents.models import ConversationModel, UserModel


def ensure_user(db: Session, user_id: str | None) -> str | None:
    if not user_id:
        return None
    normalized_user_id = _normalize_id_for_database(db, user_id)
    if not normalized_user_id:
        return None
    if db.get(UserModel, normalized_user_id) is None:
        db.add(UserModel(id=normalized_user_id, name="Workspace User", role="demo"))
        db.commit()
    return normalized_user_id


def ensure_conversation(db: Session, conversation_id: str | None, user_id: str | None) -> str | None:
    if not conversation_id:
        return None
    normalized_conversation_id = _normalize_id_for_database(db, conversation_id)
    if not normalized_conversation_id:
        return None
    normalized_user_id = ensure_user(db, user_id)
    if db.get(ConversationModel, normalized_conversation_id) is None:
        db.add(
            ConversationModel(
                id=normalized_conversation_id,
                user_id=normalized_user_id,
                title="Workspace Conversation",
                status="active",
            )
        )
        db.commit()
    return normalized_conversation_id


def prepare_runtime_identity(
    db: Session,
    user_id: str | None,
    conversation_id: str | None,
) -> tuple[str | None, str | None]:
    normalized_user_id = ensure_user(db, user_id)
    normalized_conversation_id = ensure_conversation(db, conversation_id, normalized_user_id)
    return normalized_user_id, normalized_conversation_id


def _normalize_id_for_database(db: Session, value: str) -> str | None:
    if not _is_postgresql(db):
        return value
    try:
        return str(UUID(value))
    except ValueError:
        return None


def _is_postgresql(db: Session) -> bool:
    bind = db.get_bind()
    return bind.dialect.name == "postgresql"
