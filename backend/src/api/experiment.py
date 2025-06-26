"""
Experiment API Blueprint
Handles A/B testing and experiment result recording with Swagger documentation
"""

import logging
import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields

from src.service.experiment_service import ExperimentService
from src.service.recommendation_service import RecommendationService

# Set up logging
logger = logging.getLogger(__name__)


def create_experiment_blueprint():
    """Create and configure the experiment blueprint."""
    experiment_bp = Blueprint('experiment', __name__, url_prefix='/api/experiment')

    # Configure Flask-RESTX API for this blueprint
    api = Api(
        experiment_bp,
        version='1.0.0',
        title='Experiment API',
        description='A/B testing and experiment result recording endpoints',
        doc=False  # Disable separate docs for blueprint
    )

    # Define API models for Swagger documentation
    ab_test_start_model = api.model('ABTestStart', {
        'email': fields.String(description='User email address'),
        'stress_level': fields.String(required=True, description='User stress level',
                                     enum=['無壓力', '稍微有點壓力', '中度壓力', '高度壓力', '極度壓力']),
        'emotional_state': fields.String(required=True, description='Current emotional state',
                                        enum=['平靜', '焦慮', '憂鬱', '興奮', '疲憊', '煩躁']),
        'sleep_goal': fields.String(required=True, description='Sleep goal',
                                   enum=['快速入眠', '維持整夜好眠', '改善睡眠品質', '放鬆身心']),
        'sleep_theme': fields.String(required=True, description='Sleep theme',
                                    enum=['平靜如水（穩定神經）', '森林自然（回歸原始）', '宇宙深邃（無限想像）',
                                          '溫暖懷抱（安全感）', 'AI自動推薦'])
    })

    ab_test_start_with_recommendations_model = api.model('ABTestStartWithRecommendations', {
        'session_id': fields.String(required=True, description='Session identifier'),
        'form_data': fields.Raw(required=True, description='User form data'),
        'recommendations': fields.List(fields.Raw, required=True, description='Existing recommendations')
    })

    ab_test_response_model = api.model('ABTestResponse', {
        'session_id': fields.String(description='Session identifier'),
        'user_id': fields.String(description='User identifier'),
        'form_data': fields.Raw(description='User form data'),
        'test_pairs': fields.List(fields.Raw, description='A/B test pairs'),
        'current_pair_index': fields.Integer(description='Current pair index'),
        'total_pairs': fields.Integer(description='Total number of pairs'),
        'start_time': fields.String(description='Test start timestamp'),
        'recommendation_metadata': fields.Raw(description='Recommendation metadata'),
        'error': fields.String(description='Error message if unsuccessful')
    })

    ab_test_submit_model = api.model('ABTestSubmit', {
        'session_id': fields.String(required=True, description='Session identifier'),
        'results': fields.Raw(required=True, description='Test results data'),
        'session_data': fields.Raw(required=False, description='Complete session data including test pairs')
    })

    ab_test_submit_response_model = api.model('ABTestSubmitResponse', {
        'success': fields.Boolean(description='Whether submission was successful'),
        'message': fields.String(description='Success message'),
        'session_id': fields.String(description='Session identifier'),
        'error': fields.String(description='Error message if unsuccessful')
    })

    experiment_analytics_model = api.model('ExperimentAnalytics', {
        'session_id': fields.String(description='Session identifier (if specific session)'),
        'total_sessions': fields.Integer(description='Total number of sessions'),
        'completion_rate': fields.Float(description='Test completion rate'),
        'preference_distribution': fields.Raw(description='User preference distribution'),
        'error': fields.String(description='Error message if unsuccessful')
    })

    experiment_status_model = api.model('ExperimentStatus', {
        'session_id': fields.String(description='Session identifier'),
        'status': fields.String(description='Current session status'),
        'progress': fields.Raw(description='Session progress information'),
        'error': fields.String(description='Error message if unsuccessful')
    })

    recommendation_effectiveness_model = api.model('RecommendationEffectiveness', {
        'total_choices': fields.Integer(description='Total number of choices made'),
        'recommended_chosen': fields.Integer(description='Number of times recommended tracks were chosen'),
        'random_chosen': fields.Integer(description='Number of times random tracks were chosen'),
        'recommendation_preference_rate': fields.Float(description='Rate of preference for recommended tracks (0-1)'),
        'hypothesis_supported': fields.Boolean(description='Whether the recommendation hypothesis is supported'),
        'confidence_level': fields.Float(description='Confidence level of the result (0-1)'),
        'sessions_analyzed': fields.Integer(description='Number of sessions analyzed'),
        'session_details': fields.List(fields.Raw, description='Detailed analysis per session'),
        'error': fields.String(description='Error message if unsuccessful')
    })

    # Create namespace for experiment operations
    experiment_ns = api.namespace('experiment', description='A/B testing operations')

    # A/B Test Start Resource
    @experiment_ns.route('/ab-test/start')
    class ABTestStartResource(Resource):
        @experiment_ns.expect(ab_test_start_model)
        @experiment_ns.marshal_with(ab_test_response_model)
        @experiment_ns.doc('start_ab_test')
        def post(self):
            """Start a new A/B test session (recalculates recommendations - SLOW).

            This endpoint generates new recommendations and creates A/B test pairs.
            Use this when you need fresh recommendations for testing.
            """
            try:
                data = request.get_json()

                if not data:
                    return {'error': 'No data provided'}, 400

                # Validate required fields (using snake_case to match main API)
                required_fields = ['stress_level', 'emotional_state', 'sleep_goal', 'sleep_theme']
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


    # A/B Test Start With Recommendations Resource
    @experiment_ns.route('/ab-test/start-with-recommendations')
    class ABTestStartWithRecommendationsResource(Resource):
        @experiment_ns.expect(ab_test_start_with_recommendations_model)
        @experiment_ns.marshal_with(ab_test_response_model)
        @experiment_ns.doc('start_ab_test_with_recommendations')
        def post(self):
            """Start A/B test session with existing recommendations (FAST).

            This endpoint uses pre-generated recommendations to create A/B test pairs.
            Use this when you already have recommendations and want to avoid regeneration.
            """
            try:
                data = request.get_json()

                if not data:
                    return {'error': 'No data provided'}, 400

                # Validate required fields
                required_fields = ['session_id', 'form_data', 'recommendations']
                for field in required_fields:
                    if field not in data:
                        return {'error': f'Missing required field: {field}'}, 400

                session_id = data['session_id']
                form_data = data['form_data']
                recommendations = data['recommendations']

                # Validate that we have recommendations
                if not recommendations or len(recommendations) == 0:
                    return {'error': 'No recommendations provided'}, 400

                # Create A/B test pairs using existing recommendations
                experiment_service = ExperimentService()
                test_session = experiment_service.create_ab_test_session(
                    session_id=session_id,
                    user_data=form_data,
                    recommendations=recommendations
                )

                logger.info(f"Started A/B test session with existing recommendations: {session_id}")

                return {
                    'session_id': session_id,
                    'user_id': test_session.get('user_id'),
                    'form_data': form_data,
                    'test_pairs': test_session['test_pairs'],
                    'current_pair_index': 0,
                    'total_pairs': len(test_session['test_pairs']),
                    'start_time': datetime.now().isoformat(),
                    'recommendation_metadata': {
                        'reused_existing': True,
                        'recommendations_count': len(recommendations)
                    }
                }, 200

            except Exception as e:
                logger.error(f"Error starting A/B test with recommendations: {str(e)}")
                return {'error': 'Failed to start A/B test with recommendations'}, 500

    # A/B Test Submit Resource
    @experiment_ns.route('/ab-test/submit')
    class ABTestSubmitResource(Resource):
        @experiment_ns.expect(ab_test_submit_model)
        @experiment_ns.marshal_with(ab_test_submit_response_model)
        @experiment_ns.doc('submit_ab_test_results')
        def post(self):
            """Submit A/B test results.

            This endpoint stores the results of completed A/B tests for analysis.
            Results should include user choices and preferences from the test session.
            """
            try:
                data = request.get_json()

                if not data:
                    return {'error': 'No data provided'}, 400

                # Validate required fields
                if 'session_id' not in data or 'results' not in data:
                    return {'error': 'Missing session_id or results'}, 400

                session_id = data['session_id']
                results = data['results']
                session_data = data.get('session_data')  # Optional session data

                # Validate results structure
                if not isinstance(results, dict) or 'choices' not in results:
                    return {'error': 'Invalid results format'}, 400

                # Store experiment results with optional session data
                experiment_service = ExperimentService()
                success = experiment_service.store_experiment_results(
                    session_id=session_id,
                    results=results,
                    session_data=session_data
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

    # Experiment Analytics Resource
    @experiment_ns.route('/analytics')
    @experiment_ns.route('/analytics/<string:session_id>')
    class ExperimentAnalyticsResource(Resource):
        @experiment_ns.marshal_with(experiment_analytics_model)
        @experiment_ns.doc('get_experiment_analytics')
        @experiment_ns.param('session_id', 'Optional session ID for specific session analytics')
        def get(self, session_id=None):
            """Get experiment analytics and insights.

            Returns analytics data for all experiments or a specific session.
            Includes completion rates, preference distributions, and other metrics.
            """
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

    # Experiment Status Resource
    @experiment_ns.route('/status/<string:session_id>')
    class ExperimentStatusResource(Resource):
        @experiment_ns.marshal_with(experiment_status_model)
        @experiment_ns.doc('get_experiment_status')
        @experiment_ns.param('session_id', 'The session ID to check status for')
        def get(self, session_id):
            """Get experiment session status.

            Returns the current status and progress of a specific experiment session.
            """
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

    # Recommendation Effectiveness Analysis Resource
    @experiment_ns.route('/effectiveness')
    @experiment_ns.route('/effectiveness/<string:session_id>')
    class RecommendationEffectivenessResource(Resource):
        @experiment_ns.marshal_with(recommendation_effectiveness_model)
        @experiment_ns.doc('analyze_recommendation_effectiveness')
        @experiment_ns.param('session_id', 'Optional session ID for specific session analysis')
        def get(self, session_id=None):
            """Analyze recommendation system effectiveness.

            Returns analysis of whether users prefer recommended tracks over random tracks.
            This is the key metric for validating the recommendation system's performance.
            """
            try:
                experiment_service = ExperimentService()
                analysis = experiment_service.analyze_recommendation_effectiveness(session_id)

                if 'error' in analysis:
                    return analysis, 404 if 'not found' in analysis['error'].lower() else 400

                return analysis, 200

            except Exception as e:
                logger.error(f"Error analyzing recommendation effectiveness: {str(e)}")
                return {'error': 'Failed to analyze recommendation effectiveness'}, 500

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
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    @experiment_bp.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @experiment_bp.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return experiment_bp, api


# For backward compatibility, create the blueprint instance
experiment_bp, experiment_api = create_experiment_blueprint()
