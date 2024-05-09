class APICallInfo:
    def __init__(self, api_name, api_param, call_stmt, functor):
        self.api_name = api_name
        self.api_param = api_param
        self.call_stmt = call_stmt
        self.functor = functor
    
    def delete_api_call(self, api_call_info_list: list):
        for api_call_info in api_call_info_list:
            # print("---try to replace "+api_call_info.call_stmt+"->"+self.api_param)
            if api_call_info.call_stmt in self.api_param:
                self.api_param = self.api_param.replace(api_call_info.call_stmt, "PROCESSED")
    