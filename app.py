from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json


def get_json(filename):
    """Возвращает данные из Json"""
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

