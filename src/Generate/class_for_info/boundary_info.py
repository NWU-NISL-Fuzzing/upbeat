class BoundaryInfo:
    def __init__(self, api: str, bool_expr_list: str, func_ret_list: str, arg_dict: dict):
        self.api = api
        self.bool_expr_list = bool_expr_list
        self.func_ret_list = func_ret_list
        self.arg_dict = arg_dict

    def __str__(self):
        return "api:{}\nbool:{}\nargs:{}\n".format(self.api, self.bool_expr_list, self.arg_dict)
