from socket import socket
from gravity_core_api.tests import test_settings as s
import pickle


# ТЕСТ ВИДОВ ГРУЗОВ
#test_data = {'trash_types': {'name': 'TEST123', 'wserver_id': 99, 'category': 12 ,'active': True}}

# ТЕСТ КЛИЕНТОВ
#test_data = {'companies':
#                 {'full_name':
#                      'TEST123', 'wserver_id': 1488, 'inn': 1488 ,'kpp': 1488, 'access':True, 'active': True,
#                  'id_1c': 1488}}

# ТЕСТ КАТЕГОРИЙ ГРУЗОВ
#Etest_data = {'auto': {'car_number': 'test123', 'wserver_id': 1488, 'rfid': 1488, 'active':True, 'rg_weight': 0,
 #                     'car_protocol': 'rfid', 'auto_model':0}}
#command = {}
#command['wserver_insert_command'] = test_data

#command = {'wserver_insert_command': {'auto': {'car_number': 'Х079АС102', 'car_protocol': 'rfid', 'rg_weight': 0, 'auto_model': 0, 'wserver_id': 634888, 'active': True, 'rfid': 'FFFF000140'}}}
#command = {'wserver_insert_command': {'companies': {'wserver_id': 34197, 'full_name': 'ООО "Вториндустрия"', 'short_name': 'ООО "Вториндустрия"', 'inn': '0268058847', 'kpp': None, 'active': True, 'id_1c': '000000006'}}}
#command = {'wserver_insert_command': {'update_routes': [{'id': 63, 'car_number': 'А049МС702', 'count': 1, 'active': True}, {'id': 64, 'car_number': 'А238МС702', 'count': 1, 'active': True}, {'id': 65, 'car_number': 'У431УМ102', 'count': 1, 'active': True}, {'id': 66, 'car_number': 'А085АН702', 'count': 1, 'active': True}, {'id': 67, 'car_number': 'А567АС702', 'count': 1, 'active': True}, {'id': 68, 'car_number': 'А023НУ702', 'count': 1, 'active': True}, {'id': 69, 'car_number': 'А769МС702', 'count': 1, 'active': True}, {'id': 70, 'car_number': 'С892МА02', 'count': 1, 'active': True}, {'id': 71, 'car_number': 'Н563ЕК102', 'count': 1, 'active': True}, {'id': 72, 'car_number': 'А789НМ702', 'count': 1, 'active': True}, {'id': 73, 'car_number': 'С061АК02', 'count': 1, 'active': True}, {'id': 74, 'car_number': 'Н628ВХ102', 'count': 1, 'active': True}, {'id': 75, 'car_number': 'А045АН702', 'count': 1, 'active': True}, {'id': 76, 'car_number': 'А597НМ702', 'count': 1, 'active': True}, {'id': 77, 'car_number': 'А963НМ702', 'count': 1, 'active': True}, {'id': 78, 'car_number': 'А047АН702', 'count': 1, 'active': True}, {'id': 79, 'car_number': 'А238МС702', 'count': 1, 'active': True}, {'id': 80, 'car_number': 'У431УМ102', 'count': 1, 'active': True}, {'id': 81, 'car_number': 'А085АН702', 'count': 1, 'active': True}, {'id': 82, 'car_number': 'А023НУ702', 'count': 1, 'active': True}, {'id': 83, 'car_number': 'Н563ЕК102', 'count': 1, 'active': True}, {'id': 84, 'car_number': 'А769МС702', 'count': 1, 'active': True}, {'id': 85, 'car_number': 'С892МА02', 'count': 1, 'active': True}, {'id': 86, 'car_number': 'А789НМ702', 'count': 1, 'active': True}, {'id': 87, 'car_number': 'Н628ВХ102', 'count': 1, 'active': True}, {'id': 88, 'car_number': 'А045АН702', 'count': 1, 'active': True}, {'id': 89, 'car_number': 'С061АК02', 'count': 1, 'active': True}, {'id': 90, 'car_number': 'А597НМ702', 'count': 1, 'active': True}, {'id': 91, 'car_number': 'А963НМ702', 'count': 1, 'active': True}, {'id': 92, 'car_number': 'А047АН702', 'count': 1, 'active': True}, {'id': 93, 'car_number': 'А567АС702', 'count': 1, 'active': True}]}}
command = {'wserver_insert_command': {'operators': {'wserver_id': 101, 'username': 'Эльверт', 'password': '$1$vymmxcZg$Qr3v4mnCgzRxzO4.ApW/P1', 'full_name': 'Эльверт                                            ', 'active': True}}}
command = pickle.dumps(command)
sock = socket()
sock.connect((s.api_ip, s.api_port))
sock.send(command)
response = sock.recv(1024)
response = pickle.loads(response)
print(response)