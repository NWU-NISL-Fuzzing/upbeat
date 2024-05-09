class CodeFragmentInfo:
    """
    存入和读取CodeFragment表中数据
    Attributes:
        fragment_content: 代码片段内容
        available_variables: 该片段中已声明的变量
        needful_variables: 该片段中未声明的变量
        needful_imports: 该片段需要的命名空间
        source_file: 来源
    """

    def __init__(self, fragment_content, available_variables, needful_variables, needful_imports, defined_callables, source_file):
        self.fragment_content = fragment_content
        self.available_variables = available_variables
        self.needful_variables = needful_variables
        self.needful_imports = needful_imports
        self.defined_callables = defined_callables
        self.source_file = source_file
    
    def format_to_save(self):
        defined_call_str = ""
        for s in self.defined_callables:
            if isinstance(s, str):
                defined_call_str += s
            else:
                defined_call_str += s.content
        # print(defined_call_str)
        if isinstance(self.fragment_content, str):
            return (self.fragment_content, str(self.available_variables), str(self.needful_variables), self.needful_imports, defined_call_str, self.source_file)
        else:
            return (''.join(self.fragment_content), str(self.available_variables), str(self.needful_variables), self.needful_imports, defined_call_str, self.source_file)

