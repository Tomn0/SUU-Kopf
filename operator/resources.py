import kubernetes

class K8sResource:
    def __init__(self, yamlFilename: str, namespace: str, params: dict = {}):
        self.__yamlFilename = yamlFilename
        self.__namespace = namespace
        self.__params = params
        
        self.__name = None
        self.__api = kubernetes.client.CoreV1Api()
    
    def __loadYamlData(self):
        path = os.path.join(os.path.dirname(__file__), self.__yamlFilename '.yaml')
        tmpl = open(path, 'rt').read()
        text = tmpl.format(self.__params)
        return yaml.safe_load(text)
    
    def create(self):
        raise NotImplementedError
    
    def delete(self):
        raise NotImplementedError

class Service (K8sResource):
    def create(self):
        data = self.__loadYamlData()
        self.__api.create_namespaced_service(self.__namespace, data)
        # self.__name = ??? # TODO: get created resource name
    
    def delete(self):
        if self.__name is None:
            return False
        
        self.__api.delete_namespaced_service(self.__name, self.__namespace)

        return True

