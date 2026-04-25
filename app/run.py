#!/usr/bin/env python
"""
TORIDA Backend Entry Point
==========================
Run the Flask application server.
"""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                    TORIDA API Server                      ║
    ║                   B2B Marketplace Backend                 ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Server: http://{host}:{port:<43}║
    ║  API Docs: http://{host}:{port}/api{'5000 ':<34}║
    ║  Health: http://{host}:{port}/health{'5000 ':<33}║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)
