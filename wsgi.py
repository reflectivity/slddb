from flaskr import app
import os

def appplication(env, start_response):
    return app(env, start_response)+[repr(os.environ), repr(env)]
