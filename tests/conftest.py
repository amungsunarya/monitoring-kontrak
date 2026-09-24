import os
import tempfile
import pytest  # pyright: ignore[reportMissingImports]
from app import create_app


@pytest.fixture(scope='session')
def app():
    """Test app dengan SQLite file temporary."""
    # Pakai file temporary (bukan :memory:) supaya bisa multi-connection
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    app = create_app('testing')
    app.config['DB_PATH'] = db_path

    # Init schema
    with app.app_context():
        from app.database import get_db
        db = get_db()
        with open('migrations/001_init.sql', 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()

    yield app

    # Cleanup
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def sample_user():
    return {
        'username': 'testuser',
        'password': 'test123',
        'nama': 'Test User',
        'role': 'user'
    }