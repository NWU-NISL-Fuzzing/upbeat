class DefinedVar:
    """
    对已生成的变量进行记录，避免重复生成
    """

    def __init__(self, var_name: str, var_type: str, var_size: int, var_value: str):
        self.var_name = var_name
        self.var_type = var_type
        self.var_value = var_value
        self.var_size = var_size

    def has_var_dec(self):
        return self.var_dec != ""
