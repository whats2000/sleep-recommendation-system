"""
Pipeline API Blueprint
Handles LangGraph pipeline status and monitoring endpoints with Swagger documentation
"""

from datetime import datetime
from flask import Blueprint, jsonify
from flask_restx import Api, Resource, fields

from src.service import RecommendationService
from src.utils.vector_search import get_embeddings_info


def create_pipeline_blueprint():
    """Create and configure the pipeline blueprint."""
    pipeline_bp = Blueprint('pipeline', __name__, url_prefix='/api')
    
    # Configure Flask-RESTX API for this blueprint
    api = Api(
        pipeline_bp,
        version='1.0.0',
        title='Pipeline API',
        description='LangGraph pipeline status and monitoring endpoints',
        doc=False  # Disable separate docs for blueprint
    )
    
    # Initialize service
    recommendation_service = RecommendationService()
    
    # Define API models for Swagger documentation
    pipeline_status_response_model = api.model('PipelineStatusResponse', {
        'session_id': fields.String(description='Session identifier'),
        'status': fields.String(description='Current pipeline status'),
        'current_node': fields.String(description='Currently executing node'),
        'progress': fields.Float(description='Progress percentage (0-100)'),
        'start_time': fields.String(description='Pipeline start timestamp'),
        'last_update': fields.String(description='Last update timestamp'),
        'error': fields.String(description='Error message if unsuccessful')
    })

    service_status_response_model = api.model('ServiceStatusResponse', {
        'status': fields.String(description='Overall service status'),
        'timestamp': fields.String(description='Status check timestamp'),
        'services': fields.Raw(description='Individual service statuses'),
        'embeddings_database': fields.Raw(description='Embeddings database information'),
        'error': fields.String(description='Error message if unsuccessful')
    })

    # Create namespace for pipeline operations
    pipeline_ns = api.namespace('pipeline', description='Pipeline status operations')

    # Pipeline status endpoint
    @pipeline_ns.route('/status/<string:session_id>')
    class PipelineStatusResource(Resource):
        @pipeline_ns.marshal_with(pipeline_status_response_model)
        @pipeline_ns.doc('get_pipeline_status')
        @pipeline_ns.param('session_id', 'The session ID to check status for')
        def get(self, session_id):
            """Get the status of a specific pipeline session.

            Returns the current state and progress of a LangGraph pipeline session.
            Useful for monitoring long-running recommendation generation processes.
            """
            try:
                status = recommendation_service.pipeline.get_pipeline_status(session_id)
                return status, 200
            except Exception as e:
                return {
                    "error": f"Status retrieval error: {str(e)}"
                }, 500

    # Service status endpoint
    @pipeline_bp.route('/status')
    def service_status():
        """Get the status of all service components.
        
        Returns comprehensive status information about the recommendation service,
        embeddings database, and other system components.
        """
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

    # Health check endpoint
    @pipeline_bp.route('/health')
    def health_check():
        """Health check endpoint for pipeline services."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "pipeline-api"
        })

    return pipeline_bp, api
