from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel

from secure_logging.middleware import LoggingMiddleware


class LoginPayload(BaseModel):
    username: str
    password: str


CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "8naSylHwia0rvAqa"

app = FastAPI()
app.add_middleware(LoggingMiddleware)


@app.get("/", status_code=status.HTTP_200_OK)
async def index(request: Request):
    await request.state.logger.ainfo("Hello from %s!", "index")
    return {"message": "Hello, World!"}


@app.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request, login: LoginPayload, response: Response):
    log = request.state.logger.bind(security=True)

    correct_username = login.username == CORRECT_USERNAME
    correct_password = login.password == CORRECT_PASSWORD

    if not (correct_username and correct_password):
        await log.awarning(
            "User %s has failed to log in.",
            login.username,
        )
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status": "Failure", "message": "Incorrect username or password."}
    await log.ainfo("User %s has logged in.", login.username)
    return {"status": "Success"}
