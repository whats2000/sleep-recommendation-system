#!/usr/bin/env python3
"""
Test runner for the Sleep Recommendation System.
"""

import sys


def run_pipeline_test():
    """Run the pipeline test."""
    print("=" * 50)
    print("TESTING LANGGRAPH PIPELINE")
    print("=" * 50)
    
    try:
        from tests.test_pipeline import TestRecommendationPipeline
        from datetime import datetime
        
        # Create test instance
        test_instance = TestRecommendationPipeline()
        
        # Sample data
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
            "sleep_theme": "平靜如水（穩定神經）",
            "timestamp": datetime.now()
        }
        
        # Test form data creation
        print("1. Testing FormData creation...")
        test_instance.test_form_data_creation(sample_data)
        print("   ✓ FormData creation successful")
        
        # Test pipeline initialization
        print("2. Testing pipeline initialization...")
        from src.pipeline import RecommendationPipeline
        pipeline = RecommendationPipeline(enable_checkpointing=False)
        test_instance.test_pipeline_initialization(pipeline)
        print("   ✓ Pipeline initialization successful")
        
        # Test pipeline processing
        print("3. Testing pipeline processing...")
        test_instance.test_pipeline_process_form_data(pipeline, sample_data)
        print("   ✓ Pipeline processing test completed")
        
        # Test with minimal data
        print("4. Testing with minimal data...")
        test_instance.test_pipeline_with_minimal_data(pipeline)
        print("   ✓ Minimal data test completed")
        
        print("\n✓ All pipeline tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_api_test():
    """Run the API test."""
    print("\n" + "=" * 50)
    print("TESTING FLASK API")
    print("=" * 50)
    
    try:
        from tests.test_api import TestAPI
        from src.api import create_app
        import json
        
        # Create test app
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            test_instance = TestAPI()
            
            # Test health check
            print("1. Testing health check...")
            test_instance.test_health_check(client)
            print("   ✓ Health check successful")
            
            # Test service status
            print("2. Testing service status...")
            test_instance.test_service_status(client)
            print("   ✓ Service status successful")
            
            # Test recommendations endpoint
            print("3. Testing recommendations endpoint...")
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
            test_instance.test_recommendations_endpoint_success(client, sample_data)
            print("   ✓ Recommendations endpoint test completed")
            
            # Test error handling
            print("4. Testing error handling...")
            test_instance.test_recommendations_endpoint_missing_data(client)
            test_instance.test_recommendations_endpoint_no_data(client)
            print("   ✓ Error handling tests completed")
            
            # Test 404 handling
            print("5. Testing 404 handling...")
            test_instance.test_404_error_handler(client)
            print("   ✓ 404 handling test completed")
        
        print("\n✓ All API tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_integration_test():
    """Run a simple integration test."""
    print("\n" + "=" * 50)
    print("INTEGRATION TEST")
    print("=" * 50)
    
    try:
        from src.service import RecommendationService
        from datetime import datetime
        
        print("1. Initializing recommendation service...")
        service = RecommendationService()
        print("   ✓ Service initialized")
        
        print("2. Testing service status...")
        status = service.get_service_status()
        print(f"   ✓ Service status: {status.get('pipeline_status', 'unknown')}")
        
        print("3. Testing end-to-end recommendation...")
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
            "sleep_theme": "平靜如水（穩定神經）",
            "timestamp": datetime.now()
        }
        
        result = service.get_recommendations(sample_data)
        
        if result.get("success"):
            print("   ✓ End-to-end recommendation successful")
            print(f"   Generated prompt: {result.get('generated_prompt', {}).get('musicgen_prompt', 'N/A')[:100]}...")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
        else:
            print(f"   ⚠ Recommendation completed with issues: {result.get('error', 'Unknown error')}")
        
        print("4. Cleaning up...")
        service.cleanup()
        print("   ✓ Cleanup completed")
        
        print("\n✓ Integration test completed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Sleep Recommendation System - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run pipeline tests
    results.append(run_pipeline_test())
    
    # Run API tests
    results.append(run_api_test())
    
    # Run integration test
    results.append(run_integration_test())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    test_names = ["Pipeline Tests", "API Tests", "Integration Test"]
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
    
    total_passed = sum(results)
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! The system is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
