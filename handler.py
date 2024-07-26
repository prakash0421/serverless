# handler.py
import json
import sys
import io
from flask import Request, Response
from werkzeug.middleware.proxy_fix import ProxyFix
from app import app  # Import the Flask app from app.py

def lambda_handler(event, context):
    # Prepare the WSGI environment
    environ = {
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),
        'PATH_INFO': event.get('path', '/'),
        'wsgi.input': io.BytesIO(event.get('body', '').encode('utf-8')),  # Use BytesIO for file-like object
        'CONTENT_TYPE': event.get('headers', {}).get('Content-Type', ''),
        'CONTENT_LENGTH': str(len(event.get('body', ''))),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '3000',
        'wsgi.url_scheme': 'http',
        'wsgi.version': (1, 0),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add headers to environ
    for key, value in event.get('headers', {}).items():
        environ[f'HTTP_{key.replace("-", "_").upper()}'] = value

    try:
        # Create a Flask Request object
        request = Request(environ)

        # Use the Flask WSGI app to handle the request
        app.wsgi_app = ProxyFix(app.wsgi_app)
        response = app.wsgi_app(environ, lambda s, h: None)

        # Convert the response to a proper format
        if isinstance(response, Response):
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True),
            }
        else:
            return {
                'statusCode': 500,
                'body': 'Internal server error'
            }
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }
