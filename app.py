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


@app.route('/users/<int:uid>/', methods=['GET', 'PUT', 'DELETE'])
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

        # sqlalchemy.exc.InvalidRequestError: A transaction is already begun on this Session. FTW
        # sqlalchemy.orm.exc.UnmappedInstanceError: Class 'builtins.dict' is not mapped FTW(!!!)))))) коммитим User а не new_user

        db.session.add(user)
        db.session.commit()

        return 'Данные пользователя успешно обновлены'

    elif request.method == 'DELETE':
        with db.session.begin():
            db.session.delete(user)
        return "Пользователь успешно удалён из базы!"


@app.route('/orders/', methods=['GET', 'POST'])
def orders():
    """Выводим/добавляем заказы"""
    if request.method == 'GET':
        result_list = []
        for order in db.session.query(Order).all():
            result_list.append(get_order(order))
        return jsonify(result_list)

    elif request.method == 'POST':
        data = request.json
        logging.info(f'Данные полученные через POST запрос {data}')
        allowed_keys = {'name', 'description', 'start_date', 'end_date', 'address', 'price', 'customer_id',
                        'executor_id'}
        if check_keys(data, allowed_keys):
            new_order = Order(
                name=data.get('name'),
                description=data.get('description'),
                start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),
                end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
                address=data.get('address'),
                price=data.get('price'),
                customer_id=data.get('customer_id'),
                executor_id=data.get('executor_id')
            )

            with db.session.begin():
                db.session.add(new_order)
            return "Новый пользователь добавлен в базу!"

        else:
            return 'Ключи запроса указаны неверно!'


@app.route('/orders/<int:oid>/', methods=['GET', 'PUT', 'DELETE'])
def order_by_id(oid):
    """Выводим/меняем/удаляем заказ"""
    order = db.session.query(Order).get(oid)
    if not order:
        return 'В базе нет заказа с таким ID'

    elif request.method == 'GET':
        return jsonify(get_order(order))

    elif request.method == 'PUT':
        new_order = request.json
        logging.info(f'Данные полученные через PUT запрос {new_order}')
        order.name = new_order.get('name', order.name)
        order.description = new_order.get('description', order.description)
        order.start_date = datetime.strptime(new_order.get('start_date', order.start_date), '%m/%d/%Y')
        # order.start_date = new_order.get('start_date', order.start_date)
        order.end_date = datetime.strptime(new_order.get('end_date', order.end_date), '%m/%d/%Y')
        # order.end_date = new_order.get('end_date', order.end_date)
        order.address = new_order.get('address', order.address)
        order.price = new_order.get('price', order.price)
        order.customer_id = new_order.get('customer_id', order.customer_id)
        order.executor_id = new_order.get('executor_id', order.executor_id)

        db.session.add(order)
        db.session.commit()

        return 'Данные заказа успешно обновлены'

    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return "Пользователь успешно удалён из базы!"


@app.route('/offers/', methods=['GET', 'POST'])
def offers():
    """Выводим/добавляем предложения"""
    if request.method == 'GET':
        result_list = []
        for offer in db.session.query(Offer).all():
            result_list.append(get_offer(offer))
        return jsonify(result_list)

    elif request.method == 'POST':
        data = request.json
        logging.info(f'Данные полученные через POST запрос {data}')
        allowed_keys = {'order_id', 'executor_id'}
        if check_keys(data, allowed_keys):
            new_offer = Offer(
                order_id=data.get('order_id'),
                executor_id=data.get('executor_id')
            )
            with db.session.begin():
                db.session.add(new_offer)
            return 'Новое предложение успешно добавлено в базу!'
        else:
            return 'Ключи запроса указаны неверно!'


@app.route('/offers/<int:oid>/', methods=['GET', 'PUT', 'DELETE'])
def offer_by_id(oid):
    """Выводим/меняем/удаляем предложение"""
    offer = db.session.query(Offer).get(oid)
    if not offer:
        return "В базе нет предложения с таким ID"

    elif request.method == 'GET':
        return jsonify(get_offer(offer))

    elif request.method == 'PUT':
        new_offer = request.json

        offer.order_id = new_offer.get('order_id', offer.order_id)
        offer.executor_id = new_offer.get('executor_id', offer.executor_id)

        db.session.add(offer)
        db.session.commit()
        return 'Данные предложения успешно обновлены'

    elif request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return 'Предложение успешно удалено из базы!'


if __name__ == '__main__':
    app.run()
