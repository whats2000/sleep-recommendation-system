"""
Flask application factory and main API endpoints.
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource

from src.service import RecommendationService
from src.utils.vector_search import get_embeddings_info


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Configure Flask-RESTful
    api = Api(app)
    
    # Initialize services
    recommendation_service = RecommendationService()
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "sleep-recommendation-system"
        })
    
    # Service status endpoint
    @app.route('/status', methods=['GET'])
    def service_status():
        """Get the status of all service components."""
        try:
            status = recommendation_service.get_service_status()
            embeddings_info = get_embeddings_info()
            
            return jsonify({
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "services": status,
                "embeddings_database": embeddings_info
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    # Main recommendation endpoint
    class RecommendationResource(Resource):
        def post(self):
            """Get music recommendations based on form data."""
            try:
                # Get form data from request
                try:
                    form_data = request.get_json()
                except Exception:
                    # Handle cases where Content-Type is not application/json
                    form_data = None

                if not form_data:
                    return {
                        "success": False,
                        "error": "No form data provided"
                    }, 400
                
                # Validate required fields
                required_fields = [
                    "stress_level", "emotional_state", "sleep_goal", "sleep_theme"
                ]
                
                missing_fields = [field for field in required_fields if field not in form_data]
                if missing_fields:
                    return {
                        "success": False,
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    }, 400
                
                # Set default values for optional fields
                form_data.setdefault("physical_symptoms", [])
                form_data.setdefault("sound_preferences", [])
                form_data.setdefault("sound_sensitivities", [])
                form_data.setdefault("rhythm_preference", "緩慢穩定（放鬆心跳）")
                form_data.setdefault("playback_mode", "無偏好")
                form_data.setdefault("guided_voice", "否，只需要純音樂")
                form_data.setdefault("timestamp", datetime.now())
                
                # Get recommendations
                result = recommendation_service.get_recommendations(form_data)
                
                if result.get("success"):
                    return result, 200
                else:
                    return result, 500
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"API error: {str(e)}"
                }, 500
    
    # Pipeline status endpoint
    class PipelineStatusResource(Resource):
        def get(self, session_id):
            """Get the status of a specific pipeline session."""
            try:
                status = recommendation_service.pipeline.get_pipeline_status(session_id)
                return status, 200
            except Exception as e:
                return {
                    "error": f"Status retrieval error: {str(e)}"
                }, 500
    
    # Register API resources
    api.add_resource(RecommendationResource, '/api/recommendations')
    api.add_resource(PipelineStatusResource, '/api/pipeline/status/<string:session_id>')
    
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
    
    # Cleanup on app teardown
    @app.teardown_appcontext
    def cleanup_services(error):
        """Clean up services when app context tears down."""
        try:
            recommendation_service.cleanup()
        except:
            pass
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
