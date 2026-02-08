"""
Flask application factory for ChannelSmith REST API.

This module creates and configures the Flask application with CORS support
and route registration.
"""

from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Configured Flask application instance
    """
    app = Flask(
        __name__,
        static_folder="../frontend",
        static_url_path="",
    )

    # Enable CORS for development
    CORS(app)

    # Register API blueprint
    from channelsmith.api.routes import api_bp  # pylint: disable=import-outside-toplevel

    app.register_blueprint(api_bp, url_prefix="/api")

    # Serve frontend at root
    @app.route("/")
    def index():  # pylint: disable=unused-variable
        """Serve the main HTML page."""
        return app.send_static_file("index.html")

    return app
