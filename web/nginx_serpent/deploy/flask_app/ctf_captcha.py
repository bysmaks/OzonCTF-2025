import time
import random
import string
import base64
import io
from captcha.image import ImageCaptcha
import hashlib
from config import CAPTCHA_TTL

# In-memory cache: { captcha_id: { "code": <str>, "expires": <timestamp> } }
captcha_cache = {}

def _clean_expired():
    """Remove expired captchas from the cache."""
    now = time.time()
    expired_keys = [cid for cid, data in captcha_cache.items() if data["expires"] < now]
    for key in expired_keys:
        captcha_cache.pop(key, None)

def create_captcha():
    """
    Create a new CAPTCHA challenge using the captcha library (ImageCaptcha).
    Returns:
       captcha_id (str), captcha_image (base64 str)
    """
    # Clean out expired before creating new
    _clean_expired()

    # Generate a random code for the user to type
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Create an ImageCaptcha instance. Feel free to tweak width/height/fonts:
    image_captcha = ImageCaptcha(
        width=280,
        height=90,
        fonts=None,  # You can specify a list of TTF font paths, or leave None to use defaults
    )

    # Generate the captcha image in memory
    data = image_captcha.generate(code)
    image_data = data.read()

    # Convert image bytes to base64 for embedding in HTML
    img_b64 = base64.b64encode(image_data).decode("utf-8")
    captcha_image = f"data:image/png;base64,{img_b64}"

    # Create a unique ID for this captcha
    # (use code + random + time to reduce collisions)
    raw_uid = f"{code}{random.random()}{time.time()}"
    captcha_id = hashlib.sha256(raw_uid.encode()).hexdigest()

    # Store the correct code and expiration in memory
    captcha_cache[captcha_id] = {
        "code": code,
        "expires": time.time() + CAPTCHA_TTL,
    }

    return captcha_id, captcha_image

def validate_captcha(captcha_id, user_answer):
    """
    Check if the user-supplied answer matches the stored code.
    Returns True or False.
    """
    # Clean out expired captchas first
    _clean_expired()

    # Retrieve captcha data
    data = captcha_cache.pop(captcha_id, None)
    if not data:
        # Either doesn't exist or is expired
        return False

    # Compare ignoring case, or enforce case if you prefer
    return str(user_answer).strip().upper() == data["code"].upper()

