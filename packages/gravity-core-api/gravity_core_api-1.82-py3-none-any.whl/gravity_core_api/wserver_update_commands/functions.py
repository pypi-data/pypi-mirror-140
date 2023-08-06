""" Содержит функции-обработчики команд и их вспомогательные функции """
from gravity_core_api.wserver_update_commands import settings


def trash_cat_execute(sqlshell, data, *args, **kwargs):
    """ Выполнить данные по созданию/обновлению записи о категории груза"""
    cat_name = data['cat_name']
    wserver_id = data['wserver_id']
    active = data['active']
    command = "INSERT INTO {} (cat_name, wserver_id, active) values ('{}', {}, {}) " \
              "ON CONFLICT (wserver_id) " \
              "DO UPDATE SET cat_name='{}', active={}"
    command = command.format(settings.trash_cats_tablename, cat_name,
                             wserver_id, active,
                             cat_name, active)
    response = sqlshell.try_execute(command)
    return response


def trash_type_execute(sqlshell, data, *args, **kwargs):
    """ Выполнить данные по созданию/обновлению записи о категории груза"""
    type_name = data['name']
    wserver_id = data['wserver_id']
    active = data['active']
    wserver_category = data['category']
    command = "INSERT INTO {} (name, wserver_id, active, category) values ('{}', {}, " \
              "{}, (SELECT id FROM {} WHERE wserver_id={})) " \
              "ON CONFLICT (wserver_id) " \
              "DO UPDATE SET name='{}', active={}, category=(SELECT id FROM {} WHERE wserver_id={})"
    command = command.format(settings.trash_types_tablename, type_name,
                             wserver_id,
                             active, settings.trash_cats_tablename,
                             wserver_category,
                             type_name, active, settings.trash_cats_tablename,
                             wserver_category)
    response = sqlshell.try_execute(command)
    return response


def auto_execute(sqlshell, data, *args, **kwargs):
    """ Выполнить данные по созданию/обновлению записи о машине"""
    car_number = data['car_number']
    car_protocol = data['car_protocol']
    rg_weight = data['rg_weight']
    car_model = data['auto_model']
    rfid = data['rfid']
    wserver_id = data['wserver_id']
    active = data['active']
    command = "INSERT INTO {} (car_number, rfid, id_type, rg_weight, wserver_id, auto_model, active) " \
              "values ('{}', '{}', '{}', {}, {}, {}, {}) " \
              "ON CONFLICT (wserver_id) " \
              "DO UPDATE SET car_number='{}', rfid='{}', id_type='{}', rg_weight='{}', auto_model={}, active={}"
    command = command.format(settings.auto_tablename,
                             car_number, rfid, car_protocol, rg_weight,
                             wserver_id, car_model, active,
                             car_number, rfid, car_protocol, rg_weight,
                             car_model, active)
    response = sqlshell.try_execute(command)
    return response


def clients_execute(sqlshell, data, *args, **kwargs):
    """ Выполнить данные по созданию/обновлению записи о клиенте"""
    full_name = data['full_name']
    inn = data['inn']
    kpp = data['kpp']
    esi = data['id_1c']  # external system id
    wserver_id = data['wserver_id']
    active = data['active']
    try:
        short_name = data['short_name']
    except KeyError:
        short_name = full_name
    command = "INSERT INTO {} (full_name, short_name, inn, kpp, wserver_id, active, id_1c) " \
              "values ('{}', '{}', '{}', '{}', {}, {}, '{}') " \
              "ON CONFLICT (wserver_id) " \
              "DO UPDATE SET full_name='{}', short_name='{}', inn='{}', kpp='{}', active={}, id_1c='{}'"
    command = command.format(settings.clients_tablename,
                             full_name, short_name, inn, kpp, wserver_id,
                             active, esi,
                             full_name, short_name, inn, kpp, active, esi)
    response = sqlshell.try_execute(command)
    return response


def update_route(sqlshell, data, *args, **kwargs):
    """ Обновить маршруты от AR """
    car_number = data['car_number']
    wserver_id = data['id']
    count = data['count']
    active = data['active']
    command = "INSERT INTO {} (car_number, count_expected, wserver_id, active) values ('{}', {}, {}, {}) " \
              "ON CONFLICT (wserver_id) DO UPDATE SET car_number='{}', count_expected={}, active={}"
    command = command.format(settings.routes_tablename, car_number, count,
                             wserver_id, active,
                             car_number, count, active)
    response = sqlshell.try_execute(command)
    # Добавляем в ответ wserver_id, который был при приеме
    response['wserver_id'] = wserver_id
    return response


def update_routes_execute(sqlshell, data, *args, **kwargs):
    all_responses = []
    for route in data:
        response = update_route(sqlshell, route)
        all_responses.append(response)
    return all_responses


def operators_execute(sqlshell, data, *args, **kwargs):
    """ Выполнить данные по созданию/обновлению записи об операторе"""
    username = data['username']
    password = data['password']
    active = data['active']
    command = "INSERT INTO {} (username, password, active) " \
              "values ('{}', '{}', {}) " \
              "ON CONFLICT (username) " \
              "DO UPDATE SET username='{}', password='{}', active={}"
    command = command.format(settings.operators_tablename,
                             username, password,  active,
                             username, password, active)
    response = sqlshell.try_execute(command)
    return response
