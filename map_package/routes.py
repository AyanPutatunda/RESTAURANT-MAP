from flask import render_template, jsonify, json

from map_package.dashboard import app


@app.server.route('/')
def dashboard():
    return app.index()
