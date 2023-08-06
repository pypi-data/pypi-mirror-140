""" Перспективный единый TCP API endpoint для Gravity core """
from witapi.main import WITServer
from gravity_core_api.wserver_update_commands.main import operate_update_record

class GCSE(WITServer):
    """ Gravity Core Single Endpoint """

    def __init__(self, myip, myport, sqlshell, gravity_engine, debug=False):
        super().__init__(myip, myport, sqlshell=sqlshell, without_auth=True, mark_disconnect=False, debug=debug)
        self.gravity_engine = gravity_engine
        self.sqlshell = sqlshell

    def execute_command(self, comm, values):
        if comm == 'wserver_sql_command':
            response = self.sqlshell.try_execute(values['command'])
            print('Response:', response)
        elif comm == 'wserver_insert_command':
            response = operate_update_record(self.sqlshell, values)
        else:
            response = {'status': 'failed', 'info': 'Для комманды {} не прописана логика.'.format(comm)}
        return response
