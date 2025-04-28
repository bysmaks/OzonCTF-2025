from flask import Flask, request, redirect, abort
import os
import logging
import secrets
from functools import wraps

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'CTF{sample_flag}')

REDIRECT_TOKEN = os.environ.get('REDIRECT_TOKEN', secrets.token_hex(16))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def require_redirect_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get('X-Redirect-Token') != REDIRECT_TOKEN:
            logger.warning(f"Invalid token from {request.remote_addr}")
            abort(403, description="Access denied")
        return f(*args, **kwargs)
    return decorated

@app.route('/flag')
@require_redirect_token
def get_flag():
    return FLAG

@app.route('/redirect')
def redirect_endpoint():
    target = request.args.get('target')
    if not target:
        return "Target parameter missing", 400
    
    if target != "http://internal:5000/flag":
        return "Invalid redirect target", 400
    
    logger.info("Generating redirect with token")
    
    response = redirect(target, code=302)
    response.headers['X-Redirect-Token'] = REDIRECT_TOKEN
    return response

if __name__ == '__main__':
    logger.info(f"Server started with redirect token: {REDIRECT_TOKEN}")
    app.run(host='0.0.0.0', port=5000)