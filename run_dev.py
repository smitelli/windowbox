from windowbox.application import app

app.run(host=app.config['LISTEN_INTERFACE'], port=app.config['LISTEN_PORT'])
