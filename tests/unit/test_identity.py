from backend.app.core.identity import prepare_runtime_identity
from backend.app.core.database import SessionLocal, init_database
from backend.app.documents.models import ConversationModel, UserModel


def test_prepare_runtime_identity_preserves_string_ids_for_sqlite():
    init_database()
    db = SessionLocal()
    try:
        user_id, conversation_id = prepare_runtime_identity(db, "user-1", "conv-1")

        assert user_id == "user-1"
        assert conversation_id == "conv-1"
        assert db.get(UserModel, "user-1") is not None
        assert db.get(ConversationModel, "conv-1") is not None
    finally:
        db.close()
