"""
Flask application factory and main API endpoints.
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace

from src.service import RecommendationService
from src.utils.vector_search import get_embeddings_info


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configure CORS
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

    # Configure Flask-RESTX with Swagger documentation
    api = Api(
        app,
        version='1.0.0',
        title='Sleep Recommendation System API',
        description='LangGraph-based multi-agent recommendation system for personalized sleep music',
        doc='/docs/',  # Swagger UI will be available at /docs/
        prefix='/api'
    )

    # Initialize services
    recommendation_service = RecommendationService()

    # Define API models for Swagger documentation
    form_data_model = api.model('FormData', {
        'stress_level': fields.String(required=True, description='User stress level',
                                     enum=['無壓力', '稍微有點壓力', '中度壓力', '高度壓力', '極度壓力']),
        'physical_symptoms': fields.List(fields.String, description='Physical symptoms',
                                        example=['頭腦過度活躍', '肌肉緊繃']),
        'emotional_state': fields.String(required=True, description='Current emotional state',
                                        enum=['平靜', '焦慮', '憂鬱', '興奮', '疲憊', '煩躁']),
        'sleep_goal': fields.String(required=True, description='Sleep goal',
                                   enum=['快速入眠', '維持整夜好眠', '改善睡眠品質', '放鬆身心']),
        'sound_preferences': fields.List(fields.String, description='Sound preferences',
                                        example=['樂器聲（鋼琴、古典、弦樂）']),
        'rhythm_preference': fields.String(description='Rhythm preference',
                                          enum=['超慢（冥想般，幾乎無節奏）', '緩慢穩定（放鬆心跳）', '中等節奏', '無偏好']),
        'sound_sensitivities': fields.List(fields.String, description='Sound sensitivities',
                                          example=['高頻刺耳聲']),
        'playback_mode': fields.String(description='Playback mode',
                                      enum=['循環播放', '逐漸淡出（10~20分鐘入睡）', '定時關閉', '無偏好']),
        'guided_voice': fields.String(description='Guided voice preference',
                                     enum=['是，需要引導冥想', '否，只需要純音樂']),
        'sleep_theme': fields.String(required=True, description='Sleep theme',
                                    enum=['平靜如水（穩定神經）', '森林自然（回歸原始）', '宇宙深邃（無限想像）',
                                          '溫暖懷抱（安全感）', 'AI自動推薦'])
    })

    recommendation_response_model = api.model('RecommendationResponse', {
        'success': fields.Boolean(description='Whether the request was successful'),
        'session_id': fields.String(description='Unique session identifier'),
        'generated_prompt': fields.Raw(description='Generated MusicGen prompt details'),
        'recommendations': fields.List(fields.Raw, description='List of recommended tracks'),
        'pipeline_analysis': fields.Raw(description='Analysis results from agents'),
        'processing_time': fields.Float(description='Total processing time in seconds'),
        'error': fields.String(description='Error message if unsuccessful')
    })

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
    
    # Create namespaces for better organization
    recommendations_ns = api.namespace('recommendations', description='Music recommendation operations')
    pipeline_ns = api.namespace('pipeline', description='Pipeline status operations')

    # Main recommendation endpoint
    @recommendations_ns.route('/')
    class RecommendationResource(Resource):
        @recommendations_ns.expect(form_data_model)
        @recommendations_ns.marshal_with(recommendation_response_model)
        @recommendations_ns.doc('get_recommendations')
        def post(self):
            """Get personalized music recommendations based on user form data.

            This endpoint processes user input through a LangGraph multi-agent pipeline
            to generate personalized sleep music recommendations.
            """
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
    @pipeline_ns.route('/status/<string:session_id>')
    class PipelineStatusResource(Resource):
        @pipeline_ns.doc('get_pipeline_status')
        @pipeline_ns.param('session_id', 'The session ID to check status for')
        def get(self, session_id):
            """Get the status of a specific pipeline session.

            Returns the current state and progress of a LangGraph pipeline session.
            """
            try:
                status = recommendation_service.pipeline.get_pipeline_status(session_id)
                return status, 200
            except Exception as e:
                return {
                    "error": f"Status retrieval error: {str(e)}"
                }, 500
    
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
