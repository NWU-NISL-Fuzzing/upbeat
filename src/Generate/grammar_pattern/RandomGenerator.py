import random
import json
import re

from grammar_pattern.Assignment import Assignment


class RandomGenerator:
    def __init__(self, config_path="../../config.json"):
        self.need_a_qubit_array = ['LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'FixedPoint', 'SignedLittleEndian',
                                   'LogicalRegister']
        self.basic_gate = ["H", "X", "Y", "Z", "I", "S", "T"]
        self.params = self.initParams(config_path)
        self.defined_call = []
        self.needful_namespace = ""

    def initParams(self, config_path):
        """ Get user-specified parameters. """

        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content)
        return data

    def modify_init_state(self, var_name: str, var_type: str):
        """ Add single gate to modify the initial states of qubits. """

        dec_stmt = "// Modify initial state(s) of qubit(s). \n"
        choice = random.choice([0,1,2])
        if var_type == "Qubit[]":
            if choice == 0:
                dec_stmt += "ApplyToEach("+random.choice(self.basic_gate)+", "+var_name+");\n"
            elif choice == 1:
                dec_stmt += random.choice(self.basic_gate)+"("+var_name+"[0]);\n"
        elif var_type == "Qubit":
            dec_stmt += random.choice(self.basic_gate)+"("+var_name+");\n"            
        return dec_stmt+"// Modify end. \n"

    def generate_qubit_array(self, var_name: str, var_type: str):
        """ Generate qubit array declaration for type that need Qubit[] """

        dec_stmt = ""
        # 如果是newtype数组
        if "[]" in var_type and var_type != "Qubit[]":
            for i in range(2):
                array_size = random.choice([2, 4, 6])
                dec_stmt += "use " + var_name + str(i) + "QubitArray" + " = Qubit[" + str(array_size) + "];\n"
        # 如果是newtype
        else:
            array_size = random.choice([2, 4, 6])
            dec_stmt += "use " + var_name + "QubitArray" + " = Qubit[" + str(array_size) + "];\n"
            dec_stmt += self.modify_init_state(var_name, var_type)
        return dec_stmt

    def generate_random(self, var_name: str, var_type: str):
        """ Generate variable declaration statements, and assign values randomly. """

        assign = Assignment(self.params)
        # 添加使用特殊值的概率
        if var_type in ["Int", "BigInt", "Double"]:
            prob = random.choice([0,1])
            if prob:
                var_type = "Boundary"+var_type
        # 如果是元组类型，直接调用generate_tuple
        if "(" in var_type and ")" in var_type and "=>" not in var_type and "->" not in var_type:
            return self.generate_tuple(assign, var_name, var_type)
        # 否则再进行以下步骤
        dec_stmt = ""
        # 部分类型需要声明量子比特数组
        if var_type.replace("[]", "") in self.need_a_qubit_array:
            dec_stmt += self.generate_qubit_array(var_name, var_type)
        # 生成变量值
        value = assign.generate_a_param(var_name, var_type)
        if value is None:
            with open("can_not_gen.txt", "a") as f:
                f.write("\nthis type cannot generate!" + var_type + "\n")
            return None
        if len(assign.defined_call) > 0:
            self.defined_call.extend(assign.defined_call)
        if len(assign.needful_namespace) > 0:
            self.needful_namespace += assign.needful_namespace
        # 构建变量声明语句
        dec_stmt += self.generate_random_dec(var_name, var_type, value)
        # print("===dec_stmt:\n"+dec_stmt)
        return dec_stmt
        
    def generate_random_dec(self, var_name: str, var_type: str, var_value: str):
        """ 根据传入的值构建变量声明语句 """

        # tmp_dec_stmt = ""
        if var_type == "Qubit[][]":
            tmp_dec_stmt = "use qs1 = Qubit[1];\nuse qs2 = Qubit[2];\nmutable "+var_name+" = [qs1, qs2];\n"
        elif var_type in ["Qubit", "Qubit[]"]:
            tmp_dec_stmt = "use " + var_name + " = " + var_value + ";\n"
            tmp_dec_stmt += self.modify_init_state(var_name, var_type)
        else:
            tmp_dec_stmt = "mutable " + var_name + " = " + var_value + ";\n"
        # print("check after generate random:\n"+tmp_dec_stmt)
        return tmp_dec_stmt

    def generate_tuple(self, assign: Assignment, var_name: str, var_type: str):
        """ 生成元组类型的值 """

        value = var_type
        record = []
        i = 0
        dec_stmt = ""
        for match in re.finditer("[\w\[\]]+", var_type):
            sub_var_type = match.group()
            # 如果是元组列表，例如(Int, Int)[]，将[]跳过
            # print("sub_var_type:"+sub_var_type)
            if sub_var_type == "[]":
                continue
            elif sub_var_type == "Qubit":
                dec_stmt += "use " + var_name + str(i) + " = Qubit();\n"
                sub_var_value = var_name + str(i)
            elif sub_var_type == "Qubit[]":
                array_size = random.choice([2, 4, 6])
                dec_stmt += "use " + var_name + str(i) + " = Qubit[" + str(array_size) + "];\n"
                sub_var_value = var_name + str(i)
            elif sub_var_type.replace("[]", "") in self.need_a_qubit_array:
                dec_stmt += self.generate_qubit_array(var_name + str(i), sub_var_type)
                sub_var_value = assign.generate_a_param(var_name + str(i), sub_var_type)
            else:
                sub_var_value = assign.generate_a_param(var_name + str(i), sub_var_type)
            if not sub_var_value:
                return None
            # print("sub var value:" + sub_var_value + " start-end pos:" + str(match.span()))
            record.append((sub_var_value, match.span()))
            i += 1
        var_value = var_type
        for item in reversed(record):
            var_value = var_value[:item[1][0]] + item[0] + var_value[item[1][1]:]
        if var_type.endswith("[]"):
            dec_stmt += "mutable " + var_name + " = [" + var_value[:-2] + "];\n"
        else:
            dec_stmt += "mutable " + var_name + " = " + var_value + ";\n"
        return dec_stmt


if __name__ == "__main__":
    op = RandomGenerator()
    # print(op.generate_tuple("a", "(Qubit[],Qubit[])"))
    # print(op.generate_random("a", "(Qubit[],Qubit[])"))
    # print(op.generate_random("a", "(Int, Int)[]"))
    print(op.generate_random("a", "Qubit[][]"))
