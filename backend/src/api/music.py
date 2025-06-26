"""
Music API Blueprint
Handles music database and audio serving endpoints with Swagger documentation
"""

import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_restx import Api, Resource, fields

from src.utils.vector_search import get_random_tracks


def create_music_blueprint():
    """Create and configure the music blueprint."""
    music_bp = Blueprint('music', __name__, url_prefix='/api')
    
    # Configure Flask-RESTX API for this blueprint
    api = Api(
        music_bp,
        version='1.0.0',
        title='Music API',
        description='Music database and audio serving endpoints',
        doc=False  # Disable separate docs for blueprint
    )
    
    # Define API models for Swagger documentation
    random_tracks_response_model = api.model('RandomTracksResponse', {
        'tracks': fields.List(fields.Raw, description='List of random tracks from database'),
        'count': fields.Integer(description='Number of tracks returned'),
        'error': fields.String(description='Error message if unsuccessful')
    })

    # Create namespace for music operations
    music_ns = api.namespace('music', description='Music database operations')

    # Random tracks endpoint for A/B testing
    @music_ns.route('/random')
    class RandomTracksResource(Resource):
        @music_ns.marshal_with(random_tracks_response_model)
        @music_ns.doc('get_random_tracks')
        @music_ns.param('count', 'Number of random tracks to return (max 20)', type='integer', default=5)
        def get(self):
            """Get random tracks from the music database for A/B testing comparison.

            This endpoint returns random tracks to compare against personalized recommendations.
            Used primarily for A/B testing to provide control group data.
            """
            try:
                # Get count parameter (default 5)
                count = request.args.get('count', 5, type=int)
                if count > 20:  # Limit to prevent abuse
                    count = 20

                # Get random tracks from the database
                random_tracks = get_random_tracks(count)

                if not random_tracks:
                    return {
                        "error": "No tracks available in database"
                    }, 404

                return {
                    "tracks": random_tracks,
                    "count": len(random_tracks)
                }, 200

            except Exception as e:
                print(f"Error getting random tracks: {e}")
                return {
                    "error": "Failed to get random tracks"
                }, 500

    # Audio serving endpoint (not in namespace as it's a file serving endpoint)
    @music_bp.route('/audio/<path:filename>')
    def serve_audio(filename):
        """Serve audio files for playback.
        
        This endpoint serves audio files from the data/audio directory.
        Includes security checks to prevent path traversal attacks.
        """
        try:
            # Define the audio directory (adjust path as needed)
            audio_dir = os.path.join(os.getcwd(), "data", "audio")

            # Security check - ensure filename doesn't contain path traversal
            if '..' in filename or filename.startswith('/'):
                return jsonify({"error": "Invalid filename"}), 400

            # Check if file exists
            file_path = os.path.join(audio_dir, filename)
            if not os.path.exists(file_path):
                return jsonify({"error": "Audio file not found"}), 404

            return send_from_directory(audio_dir, filename)

        except Exception as e:
            print(f"Error serving audio file: {e}")
            return jsonify({"error": "Failed to serve audio file"}), 500

    return music_bp, api
