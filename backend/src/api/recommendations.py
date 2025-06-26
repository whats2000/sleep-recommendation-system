"""
Recommendations API Blueprint
Handles music recommendation endpoints with Swagger documentation
"""

from datetime import datetime

from flask import Blueprint, request
from flask_restx import Api, Resource, fields, Namespace

from src.service import RecommendationService


def create_recommendations_blueprint():
    """Create and configure the recommendations blueprint."""
    recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api')
    
    # Configure Flask-RESTX API for this blueprint
    api = Api(
        recommendations_bp,
        version='1.0.0',
        title='Recommendations API',
        description='Music recommendation endpoints',
        doc=False  # Disable separate docs for blueprint
    )
    
    # Initialize service
    recommendation_service = RecommendationService()
    
    # Define API models for Swagger documentation
    form_data_model = api.model('FormData', {
        'email': fields.String(required=True, description='User email address'),
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

    # Create namespace for recommendations
    recommendations_ns = api.namespace('recommendations', description='Music recommendation operations')

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
                    print(f"Received form data: {form_data}")
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    # Handle cases where Content-Type is not application/json
                    form_data = None

                if not form_data:
                    print("No form data provided")
                    return {
                        "success": False,
                        "error": "No form data provided"
                    }, 400
                
                # Validate required fields
                required_fields = [
                    "email", "stress_level", "emotional_state", "sleep_goal", "sleep_theme"
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

    return recommendations_bp, api
