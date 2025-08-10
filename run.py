#!/usr/bin/env python3
"""
Russian Roulette Flask Application Runner with Socket.IO Support

This script provides an easy way to start the Flask application with Socket.IO
for real-time multiplayer functionality using threading mode.
"""

import os
import sys
from app import app, socketio

def main():
    """Main function to run the Flask application with Socket.IO."""

    print("🎯 Starting Russian Roulette Multiplayer Server...")
    print("=" * 60)

    # Check if we're in development mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']

    # Set host and port from environment or use defaults
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))

    print(f"Debug Mode: {debug_mode}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Socket.IO: Enabled")
    print(f"Real-time Multiplayer: Ready")
    print("=" * 60)
    print(f"🌐 Application will be available at: http://localhost:{port}")
    print("🎮 Multiplayer rooms supported")
    print("⚡ Real-time communication enabled")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print()

    try:
        # Run the Flask application with Socket.IO
        socketio.run(
            app,
            debug=debug_mode,
            host=host,
            port=port,
            use_reloader=debug_mode,
            log_output=debug_mode,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        print("🎯 All game rooms have been closed")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
