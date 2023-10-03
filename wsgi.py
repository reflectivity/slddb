from flaskr import app
import os

def application(env, start_response):
    print(os.environ)
    print(env)
    return app(env, start_response)
