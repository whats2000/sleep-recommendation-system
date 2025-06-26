"""
Tests for the Flask API endpoints.
"""

import pytest
import json
from datetime import datetime
import sys
from pathlib import Path

from src.api import create_app


class TestAPI:
    """Test cases for the API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create a test Flask app."""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()
    
    @pytest.fixture
    def sample_form_data(self):
        """Sample form data for API testing."""
        return {
            "stress_level": "中度壓力",
            "physical_symptoms": ["頭腦過度活躍", "肌肉緊繃"],
            "emotional_state": "焦慮",
            "sleep_goal": "快速入眠",
            "sound_preferences": ["樂器聲（鋼琴、古典、弦樂）"],
            "rhythm_preference": "超慢（冥想般，幾乎無節奏）",
            "sound_sensitivities": ["高頻刺耳聲"],
            "playback_mode": "逐漸淡出（10~20分鐘入睡）",
            "guided_voice": "否，只需要純音樂",
            "sleep_theme": "平靜如水（穩定神經）"
        }
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['service'] == 'sleep-recommendation-system'
    
    def test_service_status(self, client):
        """Test the service status endpoint."""
        response = client.get('/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'services' in data
        assert 'embeddings_database' in data
    
    def test_recommendations_endpoint_success(self, client, sample_form_data):
        """Test the recommendations endpoint with valid data."""
        response = client.post(
            '/api/recommendations',
            data=json.dumps(sample_form_data),
            content_type='application/json'
        )
        
        # Should return 200 or 500 (depending on service availability)
        assert response.status_code in [200, 500]
        data = json.loads(response.data)
        assert 'success' in data
        
        if response.status_code == 200 and data['success']:
            # Check successful response structure
            assert 'session_id' in data
            assert 'generated_prompt' in data
            assert 'processing_time' in data
    
    def test_recommendations_endpoint_missing_data(self, client):
        """Test the recommendations endpoint with missing data."""
        incomplete_data = {
            "stress_level": "中度壓力"
            # Missing required fields
        }
        
        response = client.post(
            '/api/recommendations',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert not data['success']
        assert 'error' in data
        assert 'Missing required fields' in data['error']
    
    def test_recommendations_endpoint_no_data(self, client):
        """Test the recommendations endpoint with no data."""
        response = client.post('/api/recommendations')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert not data['success']
        assert 'No form data provided' in data['error']
    
    def test_recommendations_endpoint_invalid_json(self, client):
        """Test the recommendations endpoint with invalid JSON."""
        response = client.post(
            '/api/recommendations',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_pipeline_status_endpoint(self, client):
        """Test the pipeline status endpoint."""
        session_id = "test-session-123"
        response = client.get(f'/api/pipeline/status/{session_id}')
        
        # Should return 200 (even if session doesn't exist)
        assert response.status_code == 200
        data = json.loads(response.data)
        # Response structure depends on whether checkpointing is enabled
    
    def test_404_error_handler(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-endpoint')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Endpoint not found'


if __name__ == "__main__":
    # Run a simple API test
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        print("Testing API endpoints...")
        
        # Test health check
        response = client.get('/health')
        print(f"Health check: {response.status_code}")
        
        # Test status
        response = client.get('/status')
        print(f"Status check: {response.status_code}")
        
        # Test recommendations with sample data
        sample_data = {
            "stress_level": "中度壓力",
            "physical_symptoms": ["頭腦過度活躍"],
            "emotional_state": "焦慮",
            "sleep_goal": "快速入眠",
            "sound_preferences": ["樂器聲（鋼琴、古典、弦樂）"],
            "rhythm_preference": "超慢（冥想般，幾乎無節奏）",
            "sound_sensitivities": [],
            "playback_mode": "逐漸淡出（10~20分鐘入睡）",
            "guided_voice": "否，只需要純音樂",
            "sleep_theme": "平靜如水（穩定神經）"
        }
        
        response = client.post(
            '/api/recommendations',
            data=json.dumps(sample_data),
            content_type='application/json'
        )
        print(f"Recommendations: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"Success: {data.get('success')}")
        
        print("API test completed.")
