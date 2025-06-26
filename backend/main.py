"""
Main entry point for the Sleep Recommendation System.
"""

import os

from src.api import create_app


def main():
    """Main function to run the application."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create Flask app
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Sleep Recommendation System API...")
    print(f"Server running on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    
    # Run the application
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
