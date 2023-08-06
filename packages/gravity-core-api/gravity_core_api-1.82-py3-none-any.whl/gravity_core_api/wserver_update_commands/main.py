""" Модуль для обработки комманд типа update_record """
from gravity_core_api.wserver_update_commands import settings
from traceback import format_exc


def operate_update_record(sqlshell, data, *args, **kwargs):
    print(locals())
    """ Получает словарь с данными для работы. На данный момент доступно:
     {'trash_cat': {'name': string, 'wserver_id': integer},
      'trash_type': {'name': string, 'wserver_id': integer, 'wserver_category_id': integer}.
      }
      Далее, функция обращается к словарю all_keys, где содержатся все команды в виде ключей ('trash_cat', 'trash_type')
      а в виде значения этих ключей еще один словарь, с такими ключами как, например, 'execute_funtion', которая
      принимает данные и работает с ними согласно ключу.
      То есть имеем такую структуру - поступает команда в виде {'trash_cat': {'name': 'ТКО-4', 'wserver_id':17}}.
      operate_update_record (эта функция) берет ключ первого словаря ('trash_cat'), обращается с ним в словарь all_keys,
      если находит его там, возвращает его значение 'execute_function', и передает значение ключа ('name', 'wserver_id')
      этой функции, далее возращает ответ выполнения.
      """
    for key, values in data.items():
        try:
            response = settings.all_keys[key]['execute_function'](sqlshell, values)
        # Нет такого ключа в all_keys
        except KeyError:
            response = {'status': 'failed', 'info': 'Подкоманда wserver_insert_command. '
                                                    'Для комманды {} не прописана логика.'.format(key)}
            print(format_exc())
        return response
