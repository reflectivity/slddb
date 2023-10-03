from flaskr import app
import os

def application(env, start_response):
    output=app(env, start_response)
    print(app.config)
    return output
