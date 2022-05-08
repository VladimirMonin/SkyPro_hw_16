from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy  # pip3 isntall flask sqlalchemy flask-sqlalchemy
from constant import *

from Orders import ORDERS
from Offers import OFFERS
from Users import USERS

import json

from sqlalchemy import ForeignKey


def get_json(filename):
    """Возвращает данные из Json"""
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


app = Flask(__name__)

app.config['DEBUG'] = True
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


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Нужны ли тут db.relationship?
    order = db.relationship('Order')
    executor = db.relationship('User')


def get_sql_data(users, orders, offers):
    for user in users:
        user_add = User(
            id=user['id'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            age=user['age'],
            email=user['email'],
            role=user['role'],
            phone=user['phone']
        )
        db.session.add(user_add)

    for order in orders:
        order_add = Order(
            id=order['id'],
            name=order['name'],
            description=order['description'],
            start_date=order['start_date'],
            end_date=order['end_date'],
            address=order['address'],
            price=order['price'],
            customer_id=order['customer_id'],
            executor_id=order['executor_id']
        )
        db.session.add(order_add)

    for offer in offers:
        offer_add = Offer(
            id=offer['id'],
            order_id=offer['order_id'],
            executor_id=offer['executor_id']
        )
        db.session.add(offer_add)

    db.session.commit()


def main():
    users = get_json(USERS_JSON)
    orders = get_json(ORDERS_JSON)
    offers = get_json(OFFERS_JSON)

    db.create_all()
    get_sql_data(users, orders, offers)

main()

if __name__ == '__main__':
    app.run()
