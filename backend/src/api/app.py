"""
Flask application factory and main API endpoints.
"""

from datetime import datetime

from flask import Flask, jsonify, redirect
from flask_cors import CORS
from flask_restx import Api

from src.api.recommendations import create_recommendations_blueprint
from src.api.music import create_music_blueprint
from src.api.pipeline import create_pipeline_blueprint
from src.api.experiment import create_experiment_blueprint


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configure CORS
    CORS(app, origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"])

    # Create and register blueprints
    recommendations_bp, recommendations_api = create_recommendations_blueprint()
    music_bp, music_api = create_music_blueprint()
    pipeline_bp, pipeline_api = create_pipeline_blueprint()
    experiment_bp, experiment_api = create_experiment_blueprint()

    app.register_blueprint(recommendations_bp)
    app.register_blueprint(music_bp)
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(experiment_bp)

    # Configure main Flask-RESTX API for unified Swagger documentation
    api = Api(
        app,
        version='1.0.0',
        title='Sleep Recommendation System API',
        description='LangGraph-based multi-agent recommendation system for personalized sleep music',
        doc='/docs/',  # Swagger UI will be available at /docs/
        prefix='/api'
    )

    # Add namespaces from blueprints to main API for unified documentation
    # This creates a unified Swagger documentation page
    for namespace in recommendations_api.namespaces:
        api.add_namespace(namespace, path='/recommendations')

    for namespace in music_api.namespaces:
        api.add_namespace(namespace, path='/music')

    for namespace in pipeline_api.namespaces:
        api.add_namespace(namespace, path='/pipeline')

    for namespace in experiment_api.namespaces:
        api.add_namespace(namespace, path='/experiment')

    # Default endpoint
    @app.route('/')
    def index():
        """Redirect to the Swagger documentation."""
        return redirect('/docs/')

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "sleep-recommendation-system"
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
