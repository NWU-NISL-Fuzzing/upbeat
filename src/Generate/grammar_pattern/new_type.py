from grammar_pattern.Assignment import Assignment
from grammar_pattern.RandomGenerator import RandomGenerator
from basic_operation.file_operation import initParams
from class_for_info.defined_var_info import DefinedVar

params = initParams("../config.json")
assign = Assignment(params)
rand_gen = RandomGenerator(params["work_dir"]+"/config.json")

class Complex:
    """
        newtype Complex = (Real : Double, Imag : Double);
    """

    def __init__():
        self.Real = assign.generateSmallDouble()
        self.Imag = assign.generateSmallDouble()
    
    def generate_var_value(self):
        return "Complex("+self.Real+", "+self.Imag+")"

class ReflectionPhases:
    """
        newtype ReflectionPhases = (AboutStart : Double[], AboutTarget : Double[]);
    """

    def __init__(self, start_len: int, target_len: int):
        self.AboutStart = Assignment.generateArrayWithFixedSize(params, "Double", 1, start_len)[0]
        self.AboutTarget = Assignment.generateArrayWithFixedSize(params, "Double", 1, target_len)[0]
    
    def generate_var_value(self):
        return "ReflectionPhases(AboutStart, AboutTarget)"
    
    def generate_var_dec(self, var_name: str):
        return "let "+var_name+" = "+self.generate_var_value()+";\n"

class RotationPhases:
    """
        newtype RotationPhases = (Double[]);
    """

    def __init__(self, arr_len: int):
        self.arr = Assignment.generateArrayWithFixedSize(params, "Double", 1, arr_len)

    def generate_var_value(self):
        return "RotationPhases("+self.arr+")"

class Endian:
    """
        newtype LittleEndian = (Qubit[]);
        newtype BigEndian = (Qubit[]);
        newtype PhaseLittleEndian = (Qubit[]);
    """

    def __init__(self, var_name: str, var_type: str, qubit_arr_len: int):
        self.var_name = var_name
        self.var_type = var_type
        self.qubit_arr = "Qubit["+str(qubit_arr_len)+"]"
        self.former_arr_name = var_name+"QubitArray"

    def generate_var_value(self):
        return self.var_type+"("+self.former_arr_name+")"
    
    def generate_former_dec(self):
        return "use "+ self.former_arr_name+" = "+self.qubit_arr+";\n"

    def generate_var_dec(self):
        return self.generate_former_dec()+"let "+self.var_name+" = "+self.generate_var_value()+";\n"
    
class FixedPoint:
    """
        newtype FixedPoint = (IntegerBits : Int, Register : Qubit[]);
    """

    def __init__(self, var_name: str, bits: int, register_len: int):
        self.var_name = var_name
        self.IntegerBits = str(bits)
        self.Register = "Qubit["+str(register_len)+"]"
        self.former_arr_name = var_name+"QubitArray"
    
    def generate_var_value(self):
        return "FixedPoint("+self.IntegerBits+", "+self.former_arr_name+")"
    
    def generate_former_dec(self):
        return "use "+ self.former_arr_name+" = "+self.Register+";\n"
    
    def generate_var_dec(self):
        return self.generate_former_dec()+"let "+self.var_name+" = "+self.generate_var_value()+";\n"

newtype_dict = {"ReflectionPhases":{"AboutStart":"Double[]", "AboutTarget":"Double[]"},
                "FixedPoint":{"IntegerBits":"Int", "Register":"Qubit[]"},
                "SingleQubitClifford":{"E" : "Int", "S" : "Int", "X" : "Int", "Omega" : "Int"}}

def complex_dec_generator(generate_last, mid_var_dict, defined_var_dict):
    declaration_stmt = ""
    for var_name, var_type in generate_last.items():
        real_var_name = var_name
        if "::" in var_name:
            var_name = var_name[var_name.find("::")+2:]
        if "[]" in var_type and (var_name+"ArrayLen") in mid_var_dict:
            array_len = int(mid_var_dict[var_name+"ArrayLen"])
            value, var_num = Assignment.generateArrayWithFixedSize(params, var_type.replace("[]", ""), var_type.count("[]"), array_len)
            defined_var_dict[var_name] = DefinedVar(real_var_name, var_type, array_len, value)
            if var_type == "Qubit[]":
                declaration_stmt += "use "+var_name+" = "+value+";\n"
            else:
                declaration_stmt += "let "+var_name+" = "+value+";\n"
        elif var_type == "ReflectionPhases":
            if "AboutStartArrayLen" in mid_var_dict:
                start_len = int(mid_var_dict["AboutStartArrayLen"])
            else:
                start_len = int(assign.generatePosInt())
            if "AboutTargetArrayLen" in mid_var_dict:
                target_len = int(mid_var_dict["AboutTargetArrayLen"])
            else:
                target_len = int(assign.generatePosInt())
            tmp_instance = ReflectionPhases(start_len, target_len)
            declaration_stmt += tmp_instance.generate_var_dec(var_name)
            defined_var_dict[var_name] = DefinedVar(real_var_name, var_type, 0, tmp_instance.generate_var_value())
        elif "Endian" in var_type:
            if "." in mid_var_dict[var_name+"QubitArrayLen"]:
                tmp_num = int(float(mid_var_dict[var_name+"QubitArrayLen"]))
            else:
                tmp_num = int(mid_var_dict[var_name+"QubitArrayLen"])
            tmp_instance = Endian(var_name, var_type, tmp_num)
            declaration_stmt += tmp_instance.generate_var_dec()
            defined_var_dict[var_name] = DefinedVar(real_var_name, var_type, 0, tmp_instance.generate_var_value())
        elif var_type == "FixedPoint":
            if "RegisterQubitArrayLen" in mid_var_dict:
                arr_len = int(mid_var_dict["RegisterRegisterQubitArrayLen"])
            else:
                arr_len = int(assign.generatePosInt())
            if var_name+"::IntegerBits" in defined_var_dict:
                pos = defined_var_dict[var_name+"::IntegerBits"]
            else:
                pos = int(assign.generatePosInt(arr_len))
            tmp_instance = FixedPoint(var_name, pos, arr_len)
            declaration_stmt += tmp_instance.generate_var_dec()
            defined_var_dict[var_name] = DefinedVar(real_var_name, var_type, 0, tmp_instance.generate_var_value())
        # 添加一些基本生成
        else:
            var_value = assign.generate_a_param(real_var_name, var_type)
            declaration_stmt += rand_gen.generate_random_dec(real_var_name, var_type, var_value)
            defined_var_dict[var_name] = DefinedVar(real_var_name, var_type, 0, var_value)
            # print("===declaration_stmt:\n"+declaration_stmt)
    return declaration_stmt, defined_var_dict

def get_item(var_name: str):
    instance_name = var_name[:var_name.find("::")]
    item_name = var_name[var_name.find("::")+2:]
    return instance_name, item_name

def add_items_from_newtype(relatedArgDict: dict, var_name: str):
    """ var_name的格式为xxx::yyy """

    instance_name, item_name = get_item(var_name)
    var_type = relatedArgDict[instance_name]
    relatedArgDict[var_name] = newtype_dict[var_type][item_name]
    return relatedArgDict
