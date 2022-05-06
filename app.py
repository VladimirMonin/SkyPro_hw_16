from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy  # pip3 isntall flask sqlalchemy flask-sqlalchemy

import json


def get_json(filename):
    """Возвращает данные из Json"""
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Создаем новый экземпляр Алхимии и передаём приложение где есть настройка соединения с базой ///


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    age = db.Column(db.Integer)
    email = db.Column(db.String(30))
    role = db.Column(db.String(5))
    phone = db.Column(db.String(20))


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)
    executor_id = db.Column(db.Integer)


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    executor_id = db.Column(db.Integer)


if __name__ == '__main__':
    app.run()
