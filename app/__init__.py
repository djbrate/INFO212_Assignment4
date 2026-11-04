"""Ekte Mat Online – Flask application factory.

MVC layout (CLAUDE.md, HOW: Architecture; requirements NFR-1):
  app/models/       MODEL       domain classes, rules and all data access
  app/templates/    VIEW        Jinja2 templates
  app/controllers/  CONTROLLER  Flask blueprints: shop, account, admin
"""
from __future__ import annotations

import atexit
import logging

from dotenv import load_dotenv
from flask import Flask, send_from_directory, session

from .models.cart import Cart
from .models.enums import DietaryLabel, OrderStatus, PaymentStatus
from .models.repositories.base import Repositories
from .models.services.image_service import ImageService, get_provider

log = logging.getLogger(__name__)


def create_app(config_class=None, repositories: Repositories | None = None) -> Flask:
    load_dotenv()
    from .config import Config  # imported after load_dotenv so .env values are used

    app = Flask(__name__)
    app.config.from_object(config_class or Config)

    # ---- model layer: repositories and services ---------------------------
    if repositories is None:
        repositories = _make_repositories(app)
    app.extensions["repos"] = repositories
    app.extensions["images"] = ImageService(
        app.config["UPLOAD_FOLDER"], get_provider(app.config["IMAGE_PROVIDER"], app.config["IMAGE_API_KEY"])
    )

    # ---- controllers -------------------------------------------------------
    from .controllers.account import bp as account_bp
    from .controllers.admin import bp as admin_bp
    from .controllers.shop import bp as shop_bp

    app.register_blueprint(shop_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")  # FR-A0.2

    @app.route("/media/<path:filename>")
    def media(filename):
        """Serves uploaded and generated food pictures from the upload folder."""
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    _register_view_helpers(app)
    return app


def _make_repositories(app: Flask) -> Repositories:
    if app.config["REPOSITORY"] == "fake":
        from .models.repositories.fake import make_fake_repositories

        return make_fake_repositories()

    from .models.repositories import make_neo4j_repositories
    from .models.repositories.db import Neo4jDatabase

    db = Neo4jDatabase(
        app.config["NEO4J_URI"], app.config["NEO4J_USER"], app.config["NEO4J_PASSWORD"], app.config["NEO4J_DATABASE"]
    )
    try:
        db.init_schema()
    except Exception as exc:  # the app still starts; pages show an error until Neo4j runs
        log.warning("Could not reach Neo4j at %s (%s). Is 'docker compose up -d' running?", app.config["NEO4J_URI"], exc)
    app.extensions["neo4j"] = db
    atexit.register(db.close)
    return make_neo4j_repositories(db)


def _register_view_helpers(app: Flask) -> None:
    @app.template_filter("nok")
    def nok(amount) -> str:
        """Money in NOK with a space as thousands separator, e.g. 12 450 NOK (NFR-12)."""
        try:
            return f"{int(amount):,}".replace(",", " ") + " NOK"
        except (TypeError, ValueError):
            return "–"

    @app.template_filter("isodate")
    def isodate(value) -> str:
        """Dates as YYYY-MM-DD (NFR-12)."""
        if value is None:
            return ""
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d %H:%M") if hasattr(value, "hour") else value.strftime("%Y-%m-%d")
        return str(value)

    @app.context_processor
    def globals_for_templates():
        from flask import g

        repos: Repositories = app.extensions["repos"]
        customer = None
        if session.get("customer_id"):
            customer = repos.customers.get(session["customer_id"])
        g.customer = customer
        return {
            "current_customer": customer,
            "cart_count": Cart.from_session(session).count,
            "OrderStatus": OrderStatus,
            "PaymentStatus": PaymentStatus,
            "DietaryLabel": DietaryLabel,
        }
