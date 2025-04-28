from flask import Flask, request, jsonify, make_response, render_template
import jwt
import redis
import os
import requests
from functools import wraps
import time

app = Flask(__name__)
JWT_SECRET = "vbybcnthcndj"
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')

def init_redis():
    max_retries = 5
    retry_delay = 2
    
    for i in range(max_retries):
        try:
            r = redis.Redis(
                host=REDIS_HOST,
                port=6379,
                db=0,
                socket_connect_timeout=5,
                socket_timeout=5,
                decode_responses=True
            )
            r.ping()
            
            if not r.exists("user:1"):
                r.set("user:1", "admin")
                app.logger.info("Admin user initialized")
            
            return r
        except redis.exceptions.ConnectionError as e:
            if i == max_retries - 1:
                raise
            time.sleep(retry_delay)
    
    raise redis.exceptions.ConnectionError("Could not connect to Redis")

try:
    r = init_redis()
except redis.exceptions.ConnectionError as e:
    print(f"Failed to connect to Redis: {e}")
    r = None

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return render_template('index.html', current_user=None)
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user_id = data.get('user_id')
        except:
            return render_template('index.html', current_user=None)
        
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    token = request.cookies.get('token')
    current_user = None
    if token:
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = data.get('user_id')
        except:
            pass
    return render_template('index.html', current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', current_user=None)
    
    if not r:
        return jsonify({"error": "Database connection failed"}), 500
    
    user_id = request.json.get('user_id', '').strip()
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    if len(user_id) < 1:
        return jsonify({"error": "User ID must be at least 1 character"}), 400
    
    if not user_id.isalnum():
        return jsonify({"error": "Only letters and numbers allowed"}), 400
    
    if user_id == "1":
        return jsonify({"error": "This user ID is reserved"}), 400
    
    try:
        if r.exists(f"user:{user_id}"):
            return jsonify({"error": f"User '{user_id}' already exists"}), 409
            
        r.set(f"user:{user_id}", "regular_user")
    except redis.exceptions.RedisError as e:
        return jsonify({"error": "Database operation failed"}), 500
    
    token = jwt.encode({"user_id": user_id}, JWT_SECRET, algorithm="HS256")
    
    response = make_response(jsonify({
        "message": f"User '{user_id}' registered successfully",
        "user_id": user_id,
        "redirect": f"/profile/{user_id}"
    }))
    response.set_cookie('token', token, httponly=True)
    return response

@app.route('/profile/<user_id>')
def profile(user_id):
    try:
        user_data = r.get(f"user:{user_id}")
    except redis.exceptions.RedisError:
        return render_template('profile.html', 
                            user_id=user_id,
                            role="Error",
                            hint="Database error occurred"), 500
    
    if not user_data:
        return render_template('profile.html', 
                            user_id=user_id,
                            role="Not Found",
                            hint="User does not exist"), 404
    
    hint = None
    if user_id == "1":
        hint = "Interesting profile... maybe there's a way to access it?"
    elif user_data == "admin":
        hint = "You have admin access! Check the admin panel."
    
    return render_template('profile.html',
                         user_id=user_id,
                         role=user_data,
                         hint=hint)

@app.route('/admin/status')
@auth_required
def admin_status():
    try:
        user_data = r.get(f"user:{request.user_id}")
    except redis.exceptions.RedisError:
        return render_template('profile.html',
                            user_id=request.user_id,
                            role="Error",
                            hint="Database error occurred"), 500
    
    if user_data and user_data == "admin":
        return render_template('admin.html',
                            internal_api="http://internal:5000/flag",
                            note="This endpoint is only accessible from internal network")
    return render_template('profile.html',
                         user_id=request.user_id,
                         role=user_data if user_data else "unknown",
                         hint="Admin access required"), 403

@app.route('/internal_api', methods=['POST'])
@auth_required
def internal_api():
    try:
        url = request.json.get('url')
        if not url or not url.startswith('http://internal:5000/'):
            return jsonify({"error": "Only internal URLs allowed"}), 400

        redirect_resp = requests.get(
            url,
            allow_redirects=False,
            verify=False,
            timeout=3
        )

        if redirect_resp.is_redirect:
            redirect_url = redirect_resp.headers['Location']
            
            flag_resp = requests.get(
                redirect_url,
                headers={'X-Redirect-Token': os.environ.get('REDIRECT_TOKEN')},
                allow_redirects=False,
                verify=False,
                timeout=3
            )
            return flag_resp.text
        
        return redirect_resp.text

    except Exception as e:
        app.logger.error(f"SSRF error: {str(e)}")
        return jsonify({"error": "Internal service error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)