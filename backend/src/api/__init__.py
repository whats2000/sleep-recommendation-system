"""
API layer for the recommendation system.
"""

from .app import create_app
from .recommendations import create_recommendations_blueprint
from .music import create_music_blueprint
from .pipeline import create_pipeline_blueprint
from .experiment import create_experiment_blueprint

__all__ = [
    "create_app",
    "create_recommendations_blueprint",
    "create_music_blueprint",
    "create_pipeline_blueprint",
    "create_experiment_blueprint"
]
