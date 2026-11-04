"""Settings. Secrets come from .env and are never committed (CLAUDE.md, Security basics; NFR-5)."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    REPOSITORY = os.environ.get("REPOSITORY", "neo4j")  # "neo4j" or "fake"
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
    NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE") or None
    IMAGE_PROVIDER = os.environ.get("IMAGE_PROVIDER", "stub")
    IMAGE_API_KEY = os.environ.get("IMAGE_API_KEY", "")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "static", "uploads"))
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024  # uploads above ~5 MB are refused


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    REPOSITORY = "fake"
    IMAGE_PROVIDER = "stub"
