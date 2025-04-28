from fastapi import FastAPI, Request

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)


@app.get('/')
async def root(request: Request):
    return 'ozonctf{just_hacked_another_web_with_secrets}'
