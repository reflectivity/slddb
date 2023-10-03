from flaskr import app

def application(env, start_response):
    # if apache SetEnv is used to configure mail server options
    app.config['MAIL_SERVER'] = env.get('MAIL_SERVER', 'smtp.mailtrap.io')
    app.config['MAIL_PORT'] = int(env.get('MAIL_PORT', 2525))
    app.config['MAIL_USERNAME'] = env.get('MAIL_USERNAME', '175ffa3adc24f2')
    app.config['MAIL_PASSWORD'] = env.get('MAIL_PASSWORD', '31fde10b3694db')
    return app(env, start_response)
