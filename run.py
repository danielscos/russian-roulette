#!/usr/bin/env python3
"""
Russian Roulette Flask Application Runner

This script provides an easy way to start the Flask application with proper
configuration and error handling.
"""

import os
import sys
from app import app

def main():
    """Main function to run the Flask application."""

    print("🎯 Starting Russian Roulette Game Server...")
    print("=" * 50)

    # Check if we're in development mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']

    # Set host and port from environment or use defaults
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))

    print(f"Debug Mode: {debug_mode}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("=" * 50)
    print(f"🌐 Application will be available at: http://localhost:{port}")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()

    try:
        # Run the Flask application
        app.run(
            debug=debug_mode,
            host=host,
            port=port,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
