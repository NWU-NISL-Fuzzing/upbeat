class APIInfo:
    def __init__(self, api_name, arg_info, namespace, path):
        self.api_name = api_name
        self.arg_info = arg_info
        self.namespace = namespace
        self.path = path

    def format_to_save(self):
        return (self.api_name, str(self.arg_info), self.namespace, self.path)

