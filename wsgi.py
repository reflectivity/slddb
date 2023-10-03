from flaskr import app
import os

def appplication(env, start_response):
    print(os.environ)
    print(env)
    return app(env, start_response)
