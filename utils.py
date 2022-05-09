import json
from datetime import datetime


def get_json(filename):
    """Возвращает данные из Json"""
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


def get_user(user):
    """ Данные пользователя. Получает объект DB и возвращает данные в словаре"""
    return {
        'age': user.age,
        'email': user.email,
        'first_name': user.first_name,
        'id': user.id,
        'last_name': user.last_name,
        'phone': user.phone,
        'role': user.role
    }


def get_order(order):
    """ Данные заказа. Получает объект DB и возвращает данные в словаре"""
    return {
        'id': order.id,
        'name': order.name,
        'description': order.description,
        'start_date': order.start_date,
        'end_date': order.end_date,
        'address': order.address,
        'price': order.price,
        'customer_id': order.customer_id,
        'executor_id': order.executor_id
    }


def get_offer(offer):
    """ Данные предложения. Получает объект DB и возвращает данные в словаре"""
    return {
        'id': offer.id,
        'order_id': offer.order_id,
        'executor_id': offer.executor_id
    }


def check_keys(data: dict, keys: set) -> bool:
    """Проверяем ключи на валидность"""
    for key in data:
        if key not in keys:
            return False
    else:
        return True
