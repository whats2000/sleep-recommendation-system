"""
Experiment Service
Handles A/B testing logic and experiment data management
"""

import json
import logging
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ExperimentService:
    """Service for managing A/B testing experiments"""
    
    def __init__(self):
        self.data_dir = Path("data/experiments")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths for storing experiment data
        self.sessions_file = self.data_dir / "sessions.json"
        self.results_file = self.data_dir / "results.json"
        self.analytics_file = self.data_dir / "analytics.json"
        
        # Initialize files if they don't exist
        self._init_data_files()
    
    def _init_data_files(self):
        """Initialize data files if they don't exist"""
        for file_path in [self.sessions_file, self.results_file, self.analytics_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump({}, f)

    @staticmethod
    def _load_data(file_path: Path) -> Dict:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _save_data(file_path: Path, data: Dict):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {str(e)}")
    
    def create_ab_test_session(self, session_id: str, user_data: Dict, recommendations: List[Dict], test_pairs: Optional[List[Dict]] = None) -> Dict:
        """Create a new A/B test session with music pairs"""
        try:
            # Use provided test pairs or create from recommendations
            if test_pairs is None:
                test_pairs = self._create_test_pairs(recommendations)

            # Create session data
            session_data = {
                'session_id': session_id,
                'user_id': user_data.get('user_id', str(uuid.uuid4())),
                'form_data': user_data,
                'test_pairs': test_pairs,
                'current_pair_index': 0,
                'total_pairs': len(test_pairs),
                'start_time': datetime.now().isoformat(),
                'status': 'active'
            }

            # Save session
            sessions = self._load_data(self.sessions_file)
            sessions[session_id] = session_data
            self._save_data(self.sessions_file, sessions)

            logger.info(f"Created A/B test session {session_id} with {len(test_pairs)} pairs")
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating A/B test session: {str(e)}")
            raise

    @staticmethod
    def _create_test_pairs(recommendations: List[Dict]) -> List[Dict]:
        """Create test pairs from recommendations"""
        test_pairs = []
        
        # Ensure we have enough recommendations
        if len(recommendations) < 2:
            logger.warning("Not enough recommendations for A/B testing")
            return test_pairs
        
        # Create pairs - we'll create multiple pairs for better testing
        num_pairs = min(5, len(recommendations) // 2)  # Max 5 pairs
        
        # Shuffle recommendations to randomize pairing
        shuffled_recs = recommendations.copy()
        random.shuffle(shuffled_recs)
        
        for i in range(num_pairs):
            if i * 2 + 1 < len(shuffled_recs):
                track_a = shuffled_recs[i * 2]
                track_b = shuffled_recs[i * 2 + 1]
                
                # Randomize which track is A or B
                if random.choice([True, False]):
                    track_a, track_b = track_b, track_a
                
                pair = {
                    'id': str(uuid.uuid4()),
                    'track_a': track_a,
                    'track_b': track_b,
                    'position_randomized': True
                }
                test_pairs.append(pair)
        
        return test_pairs
    
    def store_experiment_results(self, session_id: str, results: Dict, session_data: Optional[Dict] = None) -> bool:
        """Store experiment results with optional session data"""
        try:
            # Load existing results
            all_results = self._load_data(self.results_file)

            # Add timestamp and session info
            results['session_id'] = session_id
            results['submission_time'] = datetime.now().isoformat()

            # If session data is provided, store it as well
            if session_data:
                # Store the complete session data in sessions file
                sessions = self._load_data(self.sessions_file)
                sessions[session_id] = session_data
                self._save_data(self.sessions_file, sessions)

                # Add session metadata to results for easier analysis
                results['session_metadata'] = {
                    'test_pairs': session_data.get('test_pairs', []),
                    'form_data': session_data.get('form_data', {}),
                    'recommendation_metadata': session_data.get('recommendation_metadata', {})
                }
            else:
                # Update session status if session exists
                sessions = self._load_data(self.sessions_file)
                if session_id in sessions:
                    sessions[session_id]['status'] = 'completed'
                    sessions[session_id]['end_time'] = datetime.now().isoformat()
                    self._save_data(self.sessions_file, sessions)

            # Store results
            all_results[session_id] = results
            self._save_data(self.results_file, all_results)

            # Update analytics
            self._update_analytics(session_id, results)

            logger.info(f"Stored experiment results for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing experiment results: {str(e)}")
            return False

    def analyze_recommendation_effectiveness(self, session_id: Optional[str] = None) -> Dict:
        """Analyze whether users prefer recommended tracks over random tracks"""
        try:
            results = self._load_data(self.results_file)

            if session_id:
                # Analyze specific session
                if session_id not in results:
                    return {'error': 'Session not found'}
                session_results = {session_id: results[session_id]}
            else:
                # Analyze all sessions
                session_results = results

            total_choices = 0
            recommended_chosen = 0
            random_chosen = 0
            session_analyses = []

            for sid, session_data in session_results.items():
                if 'session_metadata' not in session_data:
                    continue

                test_pairs = session_data['session_metadata'].get('test_pairs', [])
                choices = session_data.get('choices', [])

                session_recommended = 0
                session_random = 0
                session_total = 0

                for choice in choices:
                    pair_id = choice['pair_id']
                    chosen_track = choice['chosen_track']  # 'A' or 'B'

                    # Find the corresponding test pair
                    test_pair = None
                    for pair in test_pairs:
                        if pair['id'] == pair_id:
                            test_pair = pair
                            break

                    if test_pair and 'recommended_track_position' in test_pair:
                        recommended_position = test_pair['recommended_track_position']  # 'A' or 'B'

                        if chosen_track == recommended_position:
                            recommended_chosen += 1
                            session_recommended += 1
                        else:
                            random_chosen += 1
                            session_random += 1

                        total_choices += 1
                        session_total += 1

                if session_total > 0:
                    session_analyses.append({
                        'session_id': sid,
                        'total_choices': session_total,
                        'recommended_chosen': session_recommended,
                        'random_chosen': session_random,
                        'recommendation_preference_rate': session_recommended / session_total
                    })

            if total_choices == 0:
                return {
                    'error': 'No valid choices found with track type information',
                    'total_sessions_analyzed': len(session_analyses)
                }

            recommendation_preference_rate = recommended_chosen / total_choices

            return {
                'total_choices': total_choices,
                'recommended_chosen': recommended_chosen,
                'random_chosen': random_chosen,
                'recommendation_preference_rate': recommendation_preference_rate,
                'hypothesis_supported': recommendation_preference_rate > 0.5,
                'confidence_level': abs(recommendation_preference_rate - 0.5) * 2,
                'sessions_analyzed': len(session_analyses),
                'session_details': session_analyses if session_id else session_analyses[:5]  # Limit details for overall analysis
            }

        except Exception as e:
            logger.error(f"Error analyzing recommendation effectiveness: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}

    def _update_analytics(self, session_id: str, results: Dict):
        """Update analytics with new experiment results"""
        try:
            analytics = self._load_data(self.analytics_file)
            
            # Initialize analytics if empty
            if not analytics:
                analytics = {
                    'total_sessions': 0,
                    'completed_sessions': 0,
                    'total_choices': 0,
                    'average_decision_time': 0,
                    'preference_patterns': {},
                    'last_updated': datetime.now().isoformat()
                }
            
            # Update counters
            analytics['completed_sessions'] += 1
            
            # Process choices
            choices = results.get('choices', [])
            analytics['total_choices'] += len(choices)
            
            # Calculate average decision time
            if choices:
                total_decision_time = sum(choice.get('decision_time_ms', 0) for choice in choices)
                avg_decision_time = total_decision_time / len(choices)
                
                # Update running average
                total_sessions = analytics['completed_sessions']
                current_avg = analytics['average_decision_time']
                analytics['average_decision_time'] = (
                    (current_avg * (total_sessions - 1) + avg_decision_time) / total_sessions
                )
            
            analytics['last_updated'] = datetime.now().isoformat()
            
            # Save updated analytics
            self._save_data(self.analytics_file, analytics)
            
        except Exception as e:
            logger.error(f"Error updating analytics: {str(e)}")
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get status of a specific session"""
        sessions = self._load_data(self.sessions_file)
        return sessions.get(session_id)
    
    def get_session_analytics(self, session_id: str) -> Optional[Dict]:
        """Get analytics for a specific session"""
        try:
            # Get session data
            session = self.get_session_status(session_id)
            if not session:
                return None
            
            # Get results
            results = self._load_data(self.results_file)
            session_results = results.get(session_id)
            
            analytics = {
                'session_id': session_id,
                'status': session.get('status'),
                'start_time': session.get('start_time'),
                'end_time': session.get('end_time'),
                'total_pairs': session.get('total_pairs', 0),
                'form_data': session.get('form_data', {}),
            }
            
            if session_results:
                choices = session_results.get('choices', [])
                analytics.update({
                    'total_choices': len(choices),
                    'completion_time': session_results.get('completion_time'),
                    'total_duration_ms': session_results.get('total_duration_ms'),
                    'choices': choices
                })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting session analytics: {str(e)}")
            return None
    
    def get_overall_analytics(self) -> Dict:
        """Get overall experiment analytics"""
        try:
            analytics = self._load_data(self.analytics_file)
            
            # Add session counts
            sessions = self._load_data(self.sessions_file)
            analytics['total_sessions'] = len(sessions)
            
            # Count active vs completed sessions
            active_sessions = sum(1 for s in sessions.values() if s.get('status') == 'active')
            analytics['active_sessions'] = active_sessions
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting overall analytics: {str(e)}")
            return {
                'error': 'Failed to load analytics',
                'total_sessions': 0,
                'completed_sessions': 0,
                'active_sessions': 0
            }
