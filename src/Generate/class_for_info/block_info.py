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
        if self.content_str in another_block:
            print("do not need this block!")
            return False
        for one_var in self.var_list:
            # print("need this var?"+one_var)
            if one_var in another_block:
                # print("yes")
                return True
        # TODO. Repeat check？
        for key in self.var_dec_dict.keys():
            # print("need this var?"+key)
            if key in another_block:
                # print("yes")
                return True
        return False

    def process_using_q(self, qubits_name: str):
        self.middle_dict[qubits_name] = "Qubit"

    def process_using_qs(self, qubits_name: str, qubits_size: str, needful_variables: dict):
        self.middle_dict[qubits_name] = "Qubit[]"
        for match_for_var in re.finditer("\w+", qubits_size):
            var = match_for_var.group()
            if var.isdigit():
                pass
            else:
                needful_variables[var] = "Int"

    def get_middle_var(self):
        needful_variables = {}
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
        for match in re.finditer(r"for (.*?) in (.*?) *{", self.content_str):
            index_str = match.group(1)
            list_str = match.group(2)
            if "(" in index_str:
                for match_for_var in re.finditer("\w+", index_str):
                    self.middle_dict[match_for_var.group()] = "'T"
            else:
                self.middle_dict[index_str] = "Int"
            # print("list_str:"+list_str)
            match_for_var = re.fullmatch("\w+", list_str)
            if match_for_var:
                # print("situation1:"+match_for_var.group())
                needful_variables[match_for_var.group()] = "Int[]"
                continue
            if ".." in list_str:
                # print("situation2:"+list_str)
                for match_for_var in re.finditer("\w+", list_str):
                    var = match_for_var.group()
                    # print("var:"+var)
                    if var.isdigit() or var == "Length":
                        pass
                    elif "Length("+var+")" in list_str:
                        needful_variables[var] = "'T[]"
                    else:
                        needful_variables[var] = "Int"
                continue
        return needful_variables
