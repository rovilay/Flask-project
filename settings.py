from flask import Flask

app = Flask(__name__)
app.config.from_envvar('APP_CONFIG')
