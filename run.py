import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables from .env file (local development only)
load_dotenv()

# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    # This is for local development only
    # Vercel will use gunicorn to run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
