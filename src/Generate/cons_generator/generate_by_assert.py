import ast
import math
import random

from basic_operation.file_operation import initParams
from DBOperation.dboperation_sqlite import DataBaseHandle
from DBOperation.save import save_into_db
from grammar_pattern.APIOperator import APIOperator
from grammar_pattern.RandomGenerator import RandomGenerator
from basic_operation.dict_operation import get_rest_args
from class_for_info.fragment_info import CodeFragmentInfo


params = initParams("../config.json")
randomVal = RandomGenerator(params["work_dir"]+"/config.json")
corpus_db = DataBaseHandle(params["corpus_db"])
reference_db = DataBaseHandle(""+params["reference_db"])
standard_api_dict = APIOperator().init_api_dict(params["work_dir"]+"/ParseAPI/data/content_all.json")

available_newtype = ['LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'Complex', 'ComplexPolar',
                            'FixedPoint', 'GeneratorIndex']
need_a_qubit_array = ['LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'FixedPoint']

# Create a true/false rotation operation
identity_rotation = {"Z-axis":["Rz"], "X-axis":["Rx"], "Y-axis":["Ry"],
                     "PauliZ":["Rz"], "PauliX":["Rx"], "PauliY":["Ry"]}
effective_rotation = {"Z-axis":["Rx", "Ry"], "X-axis":["Rz", "Ry"], "Y-axis":["Rz", "Rx"],
                      "PauliZ":["Rx", "Ry"], "PauliX":["Rz", "Ry"], "PauliY":["Rz", "Rx"]}
true_angle = ["1e-5", "PI()*2.0"]
false_angle = ["1e-4", "PI()/4.0", "PI()/2.0", "PI()"]
# Create a true/false gate
true_gate = {"Z-axis":["Z","I","S","T"],
             "X-axis":["X","I"],
             "Y-axis":["Y","I"],
             "PauliZ":["Z","I","S","T"],
             "PauliX":["X","I"],
             "PauliY":["Y","I"]}
false_gate = {"Z-axis":["X","Y"],
              "X-axis":["Z", "Y"],
              "Y-axis":["X", "Z"],
              "PauliZ":["X","Y"],
              "PauliX":["Z", "Y"],
              "PauliY":["X", "Z"]}

def rotate_by_fixed_angle(flag: bool, base: str, var_name: str, var_type: str):
    if var_type in ["FixedPoint", "LittleEndian", "BigEndian", "SignedLittleEndian"]:
        var_name += "QubitArray"
    # generate true value
    if flag:
        op = random.choice(identity_rotation[base])
        angle = random.choice(true_angle)
    # generate false value
    else:
        op = random.choice(effective_rotation[base])
        angle = random.choice(false_angle)
    # Qubit and Qubit[] need different op
    if var_type == "Qubit":
        return op+"("+angle+","+var_name+");\n"
    else:
        return op+"("+angle+","+var_name+"[0]);\n"

def rotate_by_calculated_angle(flag: bool, base: str, prob: str, tol: str, var_name: str, var_type: str):
    dec_stmt = ""
    if var_type in ["FixedPoint", "LittleEndian", "BigEndian", "SignedLittleEndian"]:
        var_name += "QubitArray"
    if base == "X-axis":
        if var_type == "Qubit":
            dec_stmt += "Ry(PI()/2.0, "+var_name+");\n"
        else:
            dec_stmt += "for q in "+var_name+"{Ry(PI()/2.0, q);}\n"
    elif base == "Y-axis":
        if var_type == "Qubit":
            dec_stmt += "Rx(-PI()/2.0, "+var_name+");\n"
        else:
            dec_stmt += "for q in "+var_name+"{Rx(-PI()/2.0, q);}\n"
    # generate true value
    if flag:
        angle = 2 * math.asin(math.sqrt(float(prob)+float(tol)))
    else:
        angle = 2 * math.asin(math.sqrt(float(prob)+float(tol))) + 0.1
    # print("angle:",angle)
    op = random.choice(effective_rotation[base])
    if var_type == "Qubit":
        dec_stmt += op+"("+str(angle)+", "+var_name+");}\n"
    else:
        dec_stmt += "for q in "+var_name+"{"+op+"("+str(angle)+", q);}\n"
    return dec_stmt

def add_gate(flag: bool, base: str, var_name: str, var_type: str):
    if var_type in ["FixedPoint", "LittleEndian", "BigEndian", "SignedLittleEndian"]:
        var_name += "QubitArray"
    # generate true value
    if flag:
        gate = random.choice(true_gate[base])
    # generate false value
    else:
        gate = random.choice(false_gate[base])
    # Qubit and Qubit[] need different op
    if var_type == "Qubit":
        return gate+"("+var_name+");\n"
    else:
        return "ApplyToEach("+gate+","+var_name+");\n"

def generate_qubit_dec(var_name, var_type):
    if var_type == "Qubit":
        return "use "+var_name+" = Qubit();\n"
    elif var_type == "Qubit[]":
        n = random.choice(["1","2"])
        return "use "+var_name+" = Qubit["+n+"];\n"
    elif var_type == "FixedPoint":
        a = random.choice(["1","2"])
        b = random.choice(["1","2"])
        return  "use "+var_name+"QubitArray = Qubit["+a+"];\nlet "+\
                var_name+" = FixedPoint("+b+", "+var_name+"QubitArray);\n"
    elif var_type in ["LittleEndian", "BigEndian"]:
        n = random.choice(["1","2"])
        return "use "+var_name+"QubitArray = Qubit["+n+"];\nmutable "+var_name+" = "+var_type+"("+var_name+"QubitArray);\n"
    else:
        raise RuntimeError("Unexpected type:"+var_type)

def query_and_generate():
    frag_list = []
    sql = "select * from QtConsStmt"
    api_list = reference_db.selectAll(sql)
    for api in api_list:
        correct_stmt, wrong_stmt = "//valid\n", "//invalid\n"
        func_name, assert_stmt, arg_info = api[1], api[2], api[3]
        arg_name, arg_type = ast.literal_eval(arg_info)
        api_info = standard_api_dict[func_name]
        open_stmt = "open " + api_info.namespace + ";\n"
        standard_api_args = api_info.get_api_args()
        rest_args = get_rest_args(standard_api_args, {arg_name: arg_type})
        other_arg_dec = ""
        for var_name, var_type in rest_args.items():
            # print("generate rest args:" + var_name + " " + var_type)
            other_arg_dec = randomVal.generate_random(var_name, var_type)
            # print("==check other_arg_dec:" + other_arg_dec)
            if other_arg_dec:
                correct_stmt += other_arg_dec
                wrong_stmt += other_arg_dec
            else:
                break
        if other_arg_dec is None:
            continue
        this_arg_dec = generate_qubit_dec(arg_name, arg_type)
        correct_stmt += this_arg_dec
        wrong_stmt += this_arg_dec
        base, result, prob, tol = ast.literal_eval(assert_stmt)
        if (result == "One" and prob == "0.0") or (result == "Zero" and prob == "1.0"):
            flag = True
        else:
            flag = False
        rotation_or_gate = random.choice([0,1,2])
        if rotation_or_gate == 0:
            correct_stmt += rotate_by_fixed_angle(flag, base, arg_name, arg_type)
            wrong_stmt += rotate_by_fixed_angle(not flag, base, arg_name, arg_type)
        elif rotation_or_gate == 1:
            correct_stmt += rotate_by_calculated_angle(flag, base, prob, tol, arg_name, arg_type)
            wrong_stmt += rotate_by_calculated_angle(not flag, base, prob, tol, arg_name, arg_type)
        else:
            correct_stmt += add_gate(flag, base, arg_name, arg_type)
            wrong_stmt += add_gate(not flag, base, arg_name, arg_type)
        reset_stmt, tmp_stmt = "", ""
        for var_name, var_type in standard_api_args.items():
            if var_type == "Qubit":
                reset_stmt += "Reset(" + var_name + ");\n"
            elif var_type == "Qubit[]":
                reset_stmt += "ResetAll(" + var_name + ");\n"
            elif var_type in need_a_qubit_array:
                reset_stmt += "ResetAll(" + var_name + "QubitArray);\n"
            elif (var_type in available_newtype) and (
                    standard_api_dict[var_type].namespace not in open_stmt):
                open_stmt += "open " + standard_api_dict[var_type].namespace + ";\n"
        if len(standard_api_args) > 0:
            call_stmt = "mutable APIResult = " + func_name + "("
            for var_name in standard_api_args.keys():
                call_stmt += var_name + ", "
            call_stmt = call_stmt[:-2] + ");\n"
        else:
            call_stmt = "mutable APIResult = " + func_name + "();"
        if "Unit" in api_info.returnType:
            output_stmt = "DumpMachine();\n"
        else:
            output_stmt = "Message($\"{APIResult}\");\n"
        correct_stmt += call_stmt + output_stmt + reset_stmt
        wrong_stmt += call_stmt + output_stmt + reset_stmt
        correct_item = CodeFragmentInfo(correct_stmt, standard_api_args, {}, open_stmt,
                                        "", "QuantumConsStmt").format_to_save()
        wrong_item = CodeFragmentInfo(wrong_stmt, standard_api_args, {}, open_stmt,
                                        "", "QuantumConsStmt").format_to_save()
        frag_list.append(correct_item)
        frag_list.append(wrong_item)
    save_into_db("/root/upbeat/data/query/corpus-v3.db", "CodeFragment_CS", frag_list)

def test():
    rotation_or_gate = random.choice([0,1])
    if rotation_or_gate == 0:
        print(rotate_by_fixed_angle(True, "AssertAllZero", "Qubit[]", "result!"))
        print(rotate_by_fixed_angle(False, "AssertAllZero", "Qubit[]", "result!"))
    else:
        print(add_gate(True, "AssertAllZero", "Qubit[]", "result!"))
        print(add_gate(False, "AssertAllZero", "Qubit[]", "result!"))

if __name__ == "__main__":
    corpus_db.createTable("CodeFragment_CS")
    query_and_generate()
    # print(rotate_by_calculated_angle(True, "Z-axis", 0.0, 0.0, "qs", "Qubit[]"))
