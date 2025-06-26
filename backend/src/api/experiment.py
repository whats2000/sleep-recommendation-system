"""
Experiment API Blueprint
Handles A/B testing and experiment result recording
"""

import logging
import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

from src.service.experiment_service import ExperimentService
from src.service.recommendation_service import RecommendationService

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
experiment_bp = Blueprint('experiment', __name__, url_prefix='/api/experiment')
experiment_api = Api(experiment_bp)

class ABTestStartResource(Resource):
    """Start a new A/B test session"""
    @staticmethod
    def post():
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            # Validate required fields
            required_fields = ['stressLevel', 'emotionalState', 'sleepGoal', 'sleepTheme']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Get recommendations for A/B testing
            recommendation_service = RecommendationService()
            recommendation_result = recommendation_service.get_recommendations(data)

            # Check if recommendation generation was successful
            if not recommendation_result.get("success"):
                return {
                    'error': 'Failed to generate recommendations',
                    'details': recommendation_result.get('error', 'Unknown error')
                }, 500

            # Extract the recommendations list from the result
            recommendations = recommendation_result.get("recommendations", [])

            # Create A/B test pairs
            experiment_service = ExperimentService()
            test_session = experiment_service.create_ab_test_session(
                session_id=session_id,
                user_data=data,
                recommendations=recommendations
            )
            
            logger.info(f"Started A/B test session: {session_id}")

            return {
                'session_id': session_id,
                'user_id': test_session.get('user_id'),
                'form_data': data,
                'test_pairs': test_session['test_pairs'],
                'current_pair_index': 0,
                'total_pairs': len(test_session['test_pairs']),
                'start_time': datetime.now().isoformat(),
                'recommendation_metadata': {
                    'pipeline_analysis': recommendation_result.get('pipeline_analysis'),
                    'processing_time': recommendation_result.get('processing_time'),
                    'generated_prompt': recommendation_result.get('generated_prompt')
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error starting A/B test: {str(e)}")
            return {'error': 'Failed to start A/B test'}, 500

class ABTestSubmitResource(Resource):
    """Submit A/B test results"""
    @staticmethod
    def post():
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            # Validate required fields
            if 'session_id' not in data or 'results' not in data:
                return {'error': 'Missing session_id or results'}, 400
            
            session_id = data['session_id']
            results = data['results']
            
            # Validate results structure
            if not isinstance(results, dict) or 'choices' not in results:
                return {'error': 'Invalid results format'}, 400
            
            # Store experiment results
            experiment_service = ExperimentService()
            success = experiment_service.store_experiment_results(
                session_id=session_id,
                results=results
            )
            
            if success:
                logger.info(f"Stored experiment results for session: {session_id}")
                return {
                    'success': True,
                    'message': 'Experiment results stored successfully',
                    'session_id': session_id
                }, 200
            else:
                return {'error': 'Failed to store experiment results'}, 500
                
        except Exception as e:
            logger.error(f"Error submitting A/B test results: {str(e)}")
            return {'error': 'Failed to submit experiment results'}, 500

class ExperimentAnalyticsResource(Resource):
    """Get experiment analytics and insights"""
    @staticmethod
    def get(session_id=None):
        try:
            experiment_service = ExperimentService()
            
            if session_id:
                # Get analytics for specific session
                analytics = experiment_service.get_session_analytics(session_id)
                if analytics:
                    return analytics, 200
                else:
                    return {'error': 'Session not found'}, 404
            else:
                # Get overall experiment analytics
                analytics = experiment_service.get_overall_analytics()
                return analytics, 200
                
        except Exception as e:
            logger.error(f"Error getting experiment analytics: {str(e)}")
            return {'error': 'Failed to get analytics'}, 500

class ExperimentStatusResource(Resource):
    """Get experiment session status"""
    @staticmethod
    def get(session_id):
        try:
            experiment_service = ExperimentService()
            status = experiment_service.get_session_status(session_id)
            
            if status:
                return status, 200
            else:
                return {'error': 'Session not found'}, 404
                
        except Exception as e:
            logger.error(f"Error getting experiment status: {str(e)}")
            return {'error': 'Failed to get session status'}, 500

# Register resources
experiment_api.add_resource(ABTestStartResource, '/ab-test/start')
experiment_api.add_resource(ABTestSubmitResource, '/ab-test/submit')
experiment_api.add_resource(ExperimentAnalyticsResource, '/analytics', '/analytics/<string:session_id>')
experiment_api.add_resource(ExperimentStatusResource, '/status/<string:session_id>')

# Health check endpoint
@experiment_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for experiment API"""
    return jsonify({
        'status': 'healthy',
        'service': 'experiment_api',
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@experiment_bp.errorhandler(400)
def bad_request():
    return jsonify({'error': 'Bad request'}), 400

@experiment_bp.errorhandler(404)
def not_found():
    return jsonify({'error': 'Not found'}), 404

@experiment_bp.errorhandler(500)
def internal_error():
    return jsonify({'error': 'Internal server error'}), 500
