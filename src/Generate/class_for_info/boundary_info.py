class BoundaryInfo:
    def __init__(self, api: str, bool_expr_list: str, func_ret_list: str, arg_dict: dict):
        """
        从FactStmt以及FailStmt表中读取数据，使用该类存储
        Attributes:
            api: 该边界条件从哪个api中提取出的
            bool_expr_list: 使用布尔表达式表示的约束（列表）
            func_ret_list: 使用特殊函数Isxxx表示的约束（列表）
            arg_dict: 该不等式语句中所需要的参数及其类型
        """

        self.api = api
        self.bool_expr_list = bool_expr_list
        self.func_ret_list = func_ret_list
        self.arg_dict = arg_dict

    def __str__(self):
        return "api:{}\nbool:{}\nargs:{}\n".format(self.api, self.bool_expr_list, self.arg_dict)
