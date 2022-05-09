from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy  # pip3 isntall flask sqlalchemy flask-sqlalchemy
from constant import *
import logging
from utils import *

logging.basicConfig(encoding='utf-8', level=logging.INFO)
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

    order = db.relationship('Order')
    executor = db.relationship('User')


def post_sql_data(users, orders, offers):
    users_list = []
    for user in users:
        users_list.append(
            User(
                id=user['id'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                age=user['age'],
                email=user['email'],
                role=user['role'],
                phone=user['phone']
            )
        )
        with db.session.begin():
            db.session.add_all(users_list)

    add_list = []
    for order in orders:
        add_list.append(
            Order(
                id=order['id'],
                name=order['name'],
                description=order['description'],
                start_date=datetime.strptime(order['start_date'], '%m/%d/%Y'),
                end_date=datetime.strptime(order['end_date'], '%m/%d/%Y'),
                address=order['address'],
                price=order['price'],
                customer_id=order['customer_id'],
                executor_id=order['executor_id']
            )
        )
        with db.session.begin():
            db.session.add_all(add_list)

    add_list = []
    for offer in offers:
        add_list.append(
            Offer(
                id=offer['id'],
                order_id=offer['order_id'],
                executor_id=offer['executor_id']
            )
        )
    with db.session.begin():
        db.session.add_all(add_list)


users = get_json(USERS_JSON)
orders = get_json(ORDERS_JSON)
offers = get_json(OFFERS_JSON)

db.create_all()
post_sql_data(users, orders, offers)


@app.route('/users/', methods=['GET', 'POST'])
def users():
    """Выводим/добавляем пользователей"""
    if request.method == "GET":
        result_list = []
        for user in db.session.query(User).all():
            result_list.append(get_user(user))
        return jsonify(result_list)

    elif request.method == "POST":
        data = request.json
        logging.info(f'Данные полученные через POST запрос: {data}')
        allowed_keys = {'age', 'email', 'first_name', 'last_name', 'phone', 'role'}
        if check_keys(data, allowed_keys):
            new_user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                age=data['age'],
                email=data['email'],
                role=data['role'],
                phone=data['phone']
            )
            with db.session.begin():
                db.session.add(new_user)
            return "Новый пользователь добавлен в базу!"

        else:
            return 'Ключи запроса указаны неверно!'


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user_by_id(uid):
    """Выводим/меняем/удаляем пользователя"""
    user = db.session.query(User).get(uid)
    if not user:
        return 'В базе нет пользователя с таким ID'

    elif request.method == 'GET':
        return jsonify(get_user(user))

    elif request.method == 'PUT':
        new_user = request.json

        user.age = new_user.get('age', user.age)  # Если значение не меняется, оставит данные как есть.
        user.email = new_user.get('email', user.email)
        user.first_name = new_user.get('first_name', user.first_name)
        user.last_name = new_user.get('last_name', user.last_name)
        user.phone = new_user.get('phone', user.phone)
        user.role = new_user.get('role', user.role)

        with db.session.begin():
            db.session.add(new_user)

        return 'Данные пользователя успешно обновлены'

    elif request.method == 'DELETE':
        with db.session.begin():
            db.session.delete(user)
        return "Пользователь успешно удалён из базы!"



# @app.route('/orders/', methods=['GET', 'POST'])
# def orders():
#     """Выводим/добавляем заказы"""
#     pass
#
#
# @app.route('/order/<int:oid>')
# def order_by_id(oid):
#     """Выводим/меняем/удаляем заказ"""
#
#     pass
#
#
# @app.route('/offers/', methods=['GET', 'POST'])
# def offers():
#     """Выводим/добавляем предложения"""
#     pass
#
#
# @app.route('/offer/<int:oid>')
# def offer_by_id(oid):
#     """Выводим/меняем/удаляем предложение"""
#     pass


if __name__ == '__main__':
    app.run()
