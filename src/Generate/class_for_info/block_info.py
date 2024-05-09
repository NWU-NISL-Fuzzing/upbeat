import re


def merge_into_one(content_list: list):
    # print("===in merge one line===")
    new_content = ""
    start_to_merge = False
    for index, line in enumerate(content_list):
        # print(index, " ", line)
        if start_to_merge:
            if line.endswith(";\n"):
                start_to_merge = False
                new_content += line.lstrip()
            else:
                new_content += line.strip()
        elif line.endswith(";\n") or line.endswith("{\n") or line.endswith("}\n"):
            new_content += line
        else:
            start_to_merge = True
            new_content += line.replace("\n", "")
        # print("now new_content:\n"+new_content)
    # print("===out merge one line===")
    return new_content


class CodeBlockInfo:
    """
    截取代码片段时划分的基础块
    Attributes:
        content_list:代码块内容列表
        content_str:代码块内容
        var_list:存放声明或者修改的变量名
        var_dec_dict:存放声明的变量字典{变量名：变量类型}
        var_use_dict:存放使用的变量字典
        middle_dict:存放局部变量字典
        api_list:包含的API列表
    """

    def __init__(self, content_list, var_list):
        self.content_list = content_list
        self.content_str = ""
        self.var_list = var_list
        self.var_dec_dict = {}
        self.var_use_dict = {}
        self.middle_dict = {}
        self.import_in_calls = ""
        self.api_list = []

    def get_content_str(self):
        self.content_str = merge_into_one(self.content_list)

    def need_this_block(self, another_block: str):
        """ 判断another_block是否与该代码块使用了相同的变量 """

        # print("this block:\n"+content_str)
        # print("another block:\n"+another_block)
        if self.content_str in another_block:
            print("do not need this block!")
            return False
        for one_var in self.var_list:
            # print("need this var?"+one_var)
            if one_var in another_block:
                # print("yes")
                return True
        # TODO.与上面的检查是否重复？
        for key in self.var_dec_dict.keys():
            # print("need this var?"+key)
            if key in another_block:
                # print("yes")
                return True
        return False

    def process_using_q(self, qubits_name: str):
        """ 处理using (q = Qubit()) """

        self.middle_dict[qubits_name] = "Qubit"

    def process_using_qs(self, qubits_name: str, qubits_size: str, needful_variables: dict):
        """ 处理using (q = Qubit[xxx])，xxx的内容可能是2/n/n-1 """

        self.middle_dict[qubits_name] = "Qubit[]"
        for match_for_var in re.finditer("\w+", qubits_size):
            var = match_for_var.group()
            if var.isdigit():
                pass
            else:
                needful_variables[var] = "Int"

    def get_middle_var(self):
        """ 获取中间变量 """

        needful_variables = {}
        # 解析using代码块
        for match in re.finditer(r"using ?\((\w+) = Qubit\(\)\)", self.content_str):
            self.process_using_q(match.group(1))
        for match in re.finditer(r"using ?\((\w+) = Qubit\[(.*)\]\)", self.content_str):
            self.process_using_qs(match.group(1), match.group(2), needful_variables)
        for match in re.finditer(r"using ?\((.*) = \((.*)\)\)", self.content_str):
            qubits_name_list = match.group(1)
            qubits_dec_list = match.group(2)
            if qubits_name_list.count(", ") != qubits_dec_list.count(", "):
                continue
            for qubits_name, qubits_dec in zip(qubits_name_list.split(", "), qubits_dec_list.split(", ")):
                if qubits_dec == "Qubit()":
                    self.middle_dict[qubits_name] = "Qubit"
                else:
                    self.process_using_qs(qubits_name, qubits_dec[6:-1], needful_variables)
        # 解析for代码块
        for match in re.finditer(r"for (.*?) in (.*?) *{", self.content_str):
            index_str = match.group(1)
            list_str = match.group(2)
            # 如果是多个索引，需要都存入middle_dict
            if "(" in index_str:
                for match_for_var in re.finditer("\w+", index_str):
                    self.middle_dict[match_for_var.group()] = "'T"
            # 否则只存储一个
            else:
                self.middle_dict[index_str] = "Int"
            # 如果是for i in intArray情况，intArray的类型为Int[]
            print("list_str:"+list_str)
            match_for_var = re.fullmatch("\w+", list_str)
            if match_for_var:
                print("situation1:"+match_for_var.group())
                needful_variables[match_for_var.group()] = "Int[]"
                continue
            # 如果是for i in 0 .. (len-1)
            if ".." in list_str:
                print("situation2:"+list_str)
                for match_for_var in re.finditer("\w+", list_str):
                    var = match_for_var.group()
                    print("var:"+var)
                    if var.isdigit() or var == "Length":
                        pass
                    elif "Length("+var+")" in list_str:
                        needful_variables[var] = "'T[]"
                    else:
                        needful_variables[var] = "Int"
                continue
            # 如果是for i in IndexRange(perm)
            # if "IndexRange(" in list_str:
            #     needful_variables[list_str[11:-1]] = "'T[]"
        # print("middle_dict:",middle_dict)
        return needful_variables
