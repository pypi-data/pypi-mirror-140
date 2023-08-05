import requests
import consul
import json
import os


class ConsulClient(object):
    _consul = None

    def __init__(self, host='127.0.0.1', port=8500,
                 application_name='webull-executor-script-service'):
        self.host = os.getenv('spring.cloud.consul.host', host)
        self.token = os.getenv('spring.cloud.consul.config.acl-token')
        self.port = os.getenv('spring.cloud.consul.port', port)
        self.service_name = os.getenv('webull.executor.application.name', application_name)
        self._consul = consul.Consul(self.host, self.port, token=self.token)

    def register(self, address, port, schema='tcp'):
        if schema.lower() == 'tcp':
            check = consul.Check.tcp(address, port, "10s")  #
        else:
            check = consul.Check.http(f'{schema}:{address}:{port}/actuator/health', "1s",
                                      "3s", "10s")

        service_id = f"{self.service_name}-{address}-{port}"
        self._consul.agent.service.register(self.service_name, service_id=service_id, address=address, port=port,
                                            check=check)

    def de_register(self, address, port):
        service_id = f"{self.service_name}-{address}-{port}"
        self._consul.agent.service.deregister(service_id)

    def get_services(self) -> list:
        return self._consul.catalog.services()[1].keys()

    def get_consul_kv(self, *args):
        """
        :param c: consul instance
        :param args: consul keys to be obtained
        :return: list of str value

        Examples:
        config_path = 'config/example
        c_keys = ['sql_host','sql_user','sql_db']
        c_values = load_consul(c,config_path,*c_keys)
        or:
        c_values = load_consul(c,config_path,'sql_host','sql_user','sql_db')
        or:
        sql_host,sql_user,sql_db = load_consul(c,config_path,*c_keys)

        Note: float or int value need to be converted later
        server_port = load_consul(c, config_path, 'server_port')
        server_port = int(server_port)
        """
        config_path = 'config/{}/'.format(self.service_name)
        args_value = []
        if not args:
            raise ValueError('Empty input consul arguments, should be a list')
        for arg in args:
            c_key = config_path + '/{}'.format(arg)
            _, c_value = self._consul.kv.get(c_key)
            if c_value:
                value = str(c_value['Value'], encoding='utf8')
                args_value.append(value)
            else:
                print('Warning: key: {} does not '
                      'exist in {}'.format(arg, config_path))

        if len(args_value) == 1:
            args_value = args_value[0]

        return args_value

    def get_vault_kv(self, vault_token, vault_version=None, *args):
        """链接consul 获取vault服务，获取vault服务参数，请求vault服务，根据k值获取对应的v值"""
        if not args:
            raise ValueError('Empty input consul arguments, should be a list')
        vault = self._consul.catalog.service('vault')
        vault_ip = vault[1][0]['ServiceAddress']
        vault_port = vault[1][0]['ServicePort']
        if vault_version:
            vault_url = f"http://{vault_ip}:{vault_port}/v{vault_version}/secret/{self.service_name}"
        else:
            vault_url = 'http://{}:{}/v1/secret/{}'.format(vault_ip, vault_port, self.service_name)
        vault_headers = {'X-Vault-Token': vault_token}
        req = requests.get(url=vault_url, headers=vault_headers)
        args_value = []
        if req.status_code == 200:
            req = json.loads(req.text)
            if 'data' in req:
                data = req['data']
                for arg in args:
                    if arg in data:
                        args_value.append(data[arg])
                    else:
                        print('key: {} not in valut'.format(arg))
            else:
                raise IndexError
        else:
            raise RuntimeError('valut connection failed, reason: {} {}'.format(req.reason, req.text))

        if len(args_value) == 1:
            args_value = args_value[0]

        return args_value
