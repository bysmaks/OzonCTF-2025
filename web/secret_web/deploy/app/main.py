import subprocess
import jwt
from fastapi import FastAPI, Request, Response, HTTPException, Form, Depends
from fastapi.templating import Jinja2Templates
from jinja2 import Environment
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
import os
import re

from config import settings
from db import database, User, TextEntry


class Auth(BaseModel):
    username: str
    password: str


class RedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 401:
            return RedirectResponse(url='/logout')
        return response


def get_current_user_from_cookie(request: Request, response: Response):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Missing JWT token")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        response.delete_cookie(key="session")
        raise HTTPException(status_code=401, detail="Invalid or expired JWT token")


def create_signed_cookie(data: dict) -> str:
    return jwt.encode(data, settings.secret_key, algorithm='HS256')


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.add_middleware(RedirectMiddleware)

templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event('startup')
async def startup():
    if not database.is_connected:
        await database.connect()


@app.on_event('shutdown')
async def shutdown():
    if database.is_connected:
        await database.disconnect()


@app.get("/", response_class=HTMLResponse)
async def form_get(
    request: Request, 
    current_user: dict = Depends(get_current_user_from_cookie)
):
    user = await User.objects.get(username=current_user['username'])
    
    entries = await TextEntry.objects.filter(user=user).all()
    
    return templates.TemplateResponse(
        "form_render.html",
        {
            "request": request,
            "entries": entries
        }
    )


jinja_env = Environment()


BLACKLISTED_COMMANDS = ['python', 'bash', 'sh', 'nc', 'socket', 'exec', 'system']

def contains_blacklisted_command(user_text: str) -> bool:
    for command in BLACKLISTED_COMMANDS:
        if re.search(rf'\b{re.escape(command)}\b', user_text, re.IGNORECASE):
            return True
    return False


@app.post("/", response_class=HTMLResponse)
async def form_post(
    request: Request,
    user_text: str = Form(...),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    if contains_blacklisted_command(user_text):
        raise HTTPException(status_code=400, detail="Input contains forbidden commands.")

    print("[User Text]:", user_text)

    user = await User.objects.get(username=current_user['username'])
    
    rendered_text = jinja_env.from_string(user_text).render()

    await TextEntry.objects.create(content=rendered_text, user=user)
    
    entries = await TextEntry.objects.filter(user=user).all()
    
    return templates.TemplateResponse(
        "form_render.html",
        {
            "request": request,
            "entries": entries
        }
    )


@app.post('/auth/register')
async def register(response: Response, auth: Auth):
    if await User.objects.get_or_none(username=auth.username) is not None:
        raise HTTPException(status_code=400, detail='Username already registered')

    user = User(username=auth.username, password=auth.password)
    await user.save()

    cookie_data = {
        'username': auth.username,
    }

    token = create_signed_cookie(cookie_data)

    response.set_cookie(key="session", value=token, httponly=True, max_age=3600)

    return {"message": "User registered successfully"}


@app.post('/auth/login')
async def login(response: Response, auth: Auth):
    user = await User.objects.get_or_none(username=auth.username)

    if user is None or user.password != auth.password:
        raise HTTPException(status_code=404, detail='Incorrect username or password')

    cookie_data = {
        'username': auth.username,
    }

    token = create_signed_cookie(cookie_data)

    response.set_cookie(key="session", value=token, httponly=True, max_age=3600)

    return {"message": "Logged in successfully"}


@app.get('/logout')
async def logout(response: Response):
    response = RedirectResponse(url='/login')
    response.delete_cookie(key="session")
    return response


@app.get('/login', response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(request, 'login.html')


@app.get('/register', response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(request, 'register.html')
