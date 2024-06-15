import re
import json 
import random

from basic_operation.file_operation import *
from basic_operation.dict_operation import get_undefined_args
from class_for_info.constraint_tree import ConstraintTree, ConstraintTreeOp
from class_for_info.defined_var_info import DefinedVar
from grammar_pattern.APIOperator import APIOperator
from grammar_pattern.Assignment import Assignment
from grammar_pattern.new_type import complex_dec_generator, add_items_from_newtype
from grammar_pattern.RandomGenerator import RandomGenerator
from cons_generator.parse_boundary_expr import *
from cons_generator.calculate import calculate_math_expr

params = initParams("../config.json")
assign = Assignment(params)
standard_api_dict = APIOperator().init_api_dict(params["work_dir"]+"/ParseAPI/data/content_all.json")

regex_for_length = r"Length\(([\w:]+?)!?\)"


class GenerateCorrectAndWrong:
    def __init__(self):
        self.need_a_qubit_array = ['LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'FixedPoint']
        self.need_a_classical_array = ['ReflectionPhases', 'RotationPhases']
        self.var_num = 0
        self.correct_mid_dict = {}
        self.wrong_mid_dict = {}
        self.correct = True
        self.defined_var_dict = {}
    
    def get_var_name(self, content_of_node):
        """ 对节点内容进行处理，获取真正的变量名，目前识别的情况为Length(xxx)->xxx """

        # print("get var name:"+content_of_node)
        var_name, var_type = "", ""
        length_match = re.search(regex_for_length, content_of_node)
        if length_match:
            var_name = length_match.group(1)
        else:
            var_name = content_of_node
        return var_name
    
    def generate_declaration(self, var_name, var_type, value):
        """ 组装声明语句 """

        final_fragment = ""
        if var_type == "Qubit[]" and "Qubit[" in value:
            final_fragment += "use " + var_name + " = " + value + ";\n"
        elif var_type == "Qubit[]" and "Qubit[" not in value:
            final_fragment += "mutable " + var_name + "Len = " + value + ";\n"
            final_fragment += "use " + var_name + " = Qubit[" + var_name + "Len];\n"
        elif "Endian" in var_type and re.match(r"[0-9 +=/*%^<>]+", value):
            final_fragment += "mutable " + var_name + "Len = " + value + ";\n"
            final_fragment += "use " + var_name + "QubitArray = Qubit[" + var_name + "Len];\n"
            final_fragment += "mutable " + var_name + " = " + var_type + "(" + var_name + "QubitArray);\n"
        else:
            final_fragment += "mutable " + var_name + " = " + value + ";\n"
        return final_fragment
    
    def process_newtype_attr(self, var_name: str, relatedArgDict: dict):
        """ 处理特殊情况：当访问的是newtype的属性时，需要在relatedArgDict中添加一项指明其类型 """

        # print("before process newtype attr:"+var_name+" "+str(relatedArgDict))
        if "::" in var_name:
            relatedArgDict = add_items_from_newtype(relatedArgDict, var_name)
            var_type = relatedArgDict[var_name]
            var_name = var_name[var_name.find("::")+2:]
        elif "*" in var_name or "+" in var_name:
            tmp_match = re.search(r"Length\(([a-zA-Z0-9_]+)!*\)", var_name)
            if tmp_match:
                var_name = tmp_match.group(1)
                var_type = relatedArgDict[var_name]
            # else:
            #     print("===special situation:"+var_name)
        elif "Length(LittleEndian(" in var_name:
            tmp_match = re.search("Length\(LittleEndian\((\w+)!*\)!\)", var_name)
            if tmp_match:
                var_name = tmp_match.group(1)
                var_type = relatedArgDict[var_name]
        else:
            var_type = relatedArgDict[var_name]
        # print("after process newtype attr:"+var_name+" "+var_type+" "+str(relatedArgDict))
        return var_name, var_type

    def generate_random_value(self, one_cons_tree: ConstraintTree, select_node: ConstraintTree, relatedArgDict: dict):
        """ 根据指定类型生成随机值，因为要替换节点，所以不使用Random类 """

        final_fragment = ""
        
        # 获取变量类型
        content_of_node = select_node.rootNode
        var_name = self.get_var_name(content_of_node)
        # print("===var_name:"+var_name)

        raw_var_name = var_name
        var_name, var_type = self.process_newtype_attr(var_name, relatedArgDict)
        
        # 部分类型需要声明量子比特数组
        array_size = 0
        if var_type in self.need_a_qubit_array:
            array_size = random.choice([2, 4, 6])
            final_fragment += "use " + var_name + "QubitArray = Qubit[" + str(array_size) + "];\n"
            one_cons_tree.setRightNode(ConstraintTree(str(array_size)), "True")
        
        # 生成变量值
        if var_type.count("[]") == 0:
            value = assign.generate_a_param(var_name, var_type)
            if value == None:
                with open("log.txt",'a') as f:
                    f.write("\n[SELF-DEFINED]failed in generate_random_value,this type cannot generate."+var_type+"\n")
                return None
            if var_type not in self.need_a_qubit_array:
                one_cons_tree.setRightNode(ConstraintTree(value), "True")
                self.defined_var_dict[var_name] = DefinedVar(raw_var_name, var_type, 0, value)
            else:
                self.defined_var_dict[var_name] = DefinedVar(raw_var_name, var_type, array_size, value)
        elif var_type.count("[]") == 1:
            size = random.choice([2, 4, 6])
            value, self.var_num = assign.generateArrayWithFixedSize(params, var_type.replace("[]", ""), 1,
                                                                        size, self.var_num)
            # print("check value:"+value)
            self.defined_var_dict[var_name] = DefinedVar(raw_var_name, var_type, size, value)
            one_cons_tree.setRightNode(ConstraintTree(str(size)), "True")
        else:
            with open("log.txt",'a') as f:
                f.write("\n[SELF-DEFINED]failed in generate_random_value,cannot process two+ dimension array.")
            return None
        
        # 构建变量声明语句
        final_fragment += self.generate_declaration(var_name, var_type, value)
        # print("check after generate random:\n"+final_fragment)
        
        return final_fragment

    def plus(self, certain_value, uncertain_value, var_type, former_stmt: str):
        """ 对>certain_value的情况取合理值 """

        if var_type == "Int":
            final_stmt = "let "+uncertain_value+" = "+certain_value + " + 1;\n"
            self.defined_var_dict[uncertain_value] = DefinedVar(uncertain_value, var_type, 0, calculate_math_expr(certain_value + " + 1"))
        elif var_type == "Double":
            final_stmt = "let "+uncertain_value+" = "+certain_value + " + 0.1;\n"
            self.defined_var_dict[uncertain_value] = DefinedVar(uncertain_value, var_type, 0, calculate_math_expr(certain_value + " + 0.1"))
        elif var_type == "BigInt":
            final_stmt = "let "+uncertain_value+" = "+certain_value + " + 1L;\n"
            self.defined_var_dict[uncertain_value] = DefinedVar(uncertain_value, var_type, 0, calculate_math_expr(certain_value + " + 1")+"L")
        elif "[]" in var_type or var_type in self.need_a_classical_array:
            final_stmt = "let "+uncertain_value+"ArrayLen = "+certain_value+" + 1;\n"
            if self.correct:
                self.correct_mid_dict[uncertain_value+"ArrayLen"] = calculate_math_expr(certain_value+" + 1")
            else:
                self.wrong_mid_dict[uncertain_value+"ArrayLen"] = calculate_math_expr(certain_value+" + 1")
            # print(">>>correct_mid_dict:",self.correct_mid_dict)
            # print(">>>wrong_mid_dict:",self.wrong_mid_dict)
        elif var_type in self.need_a_qubit_array:
            final_stmt = "let "+uncertain_value+"QubitArrayLen = "+certain_value+" + 1;\n"
            if self.correct:
                self.correct_mid_dict[uncertain_value+"QubitArrayLen"] = calculate_math_expr(certain_value+" + 1")
            else:
                self.wrong_mid_dict[uncertain_value+"QubitArrayLen"] = calculate_math_expr(certain_value+" + 1")
        else:
            return None
        
        return final_stmt

    def minus(self, certain_value, uncertain_value, var_type, former_stmt: str):
        """ 对<certain_value的情况取合理值 """

        if var_type == "Int":
            final_stmt = "let "+uncertain_value+" = "+certain_value + " - 1;\n"
            self.defined_var_dict[uncertain_value] = DefinedVar(uncertain_value, var_type, 0, calculate_math_expr(certain_value + " - 1"))
        elif var_type == "Double":
            final_stmt = "let "+uncertain_value+" = "+certain_value + " - 0.1;\n"
            self.defined_var_dict[uncertain_value] = DefinedVar(uncertain_value, var_type, 0, calculate_math_expr(certain_value + " - 0.1"))
        elif var_type == "BigInt":
            final_stmt = "let "+uncertain_value+" = "+certain_value + " - 1L;\n"
            self.defined_var_dict[uncertain_value] = DefinedVar(uncertain_value, var_type, 0, calculate_math_expr(certain_value + " - 1")+"L")
        elif "[]" in var_type or var_type in self.need_a_classical_array:
            final_stmt = "let "+uncertain_value+"ArrayLen = "+certain_value+" - 1;\n"
            if self.correct:
                self.correct_mid_dict[uncertain_value+"ArrayLen"] = calculate_math_expr(certain_value+" - 1")
            else:
                self.wrong_mid_dict[uncertain_value+"ArrayLen"] = calculate_math_expr(certain_value+" - 1")
        elif var_type in self.need_a_qubit_array:
            final_stmt = "let "+uncertain_value+"QubitArrayLen = "+certain_value+" - 1;\n"
            if self.correct:
                self.correct_mid_dict[uncertain_value+"QubitArrayLen"] = calculate_math_expr(certain_value+" - 1")
            else:
                self.wrong_mid_dict[uncertain_value+"QubitArrayLen"] = calculate_math_expr(certain_value+" - 1")
        else:
            return None
        
        return final_stmt

    def equal(self, certain_value, uncertain_value, var_type, former_stmt: str):
        """ 对=certain_value的情况取合理值 """

        # print("var_type:"+var_type+" uncertain_value:"+uncertain_value)
        if var_type in ["Int", "Double", "BigInt"]:
            final_stmt = "let "+uncertain_value+" = "+certain_value + ";\n"
            self.defined_var_dict[uncertain_value] = DefinedVar(uncertain_value, var_type, 0, certain_value)
        elif "[]" in var_type or var_type in self.need_a_classical_array:
            final_stmt = "let "+uncertain_value+"ArrayLen = "+certain_value+";\n"
            if self.correct:
                self.correct_mid_dict[uncertain_value+"ArrayLen"] = certain_value
            else:
                self.wrong_mid_dict[uncertain_value+"ArrayLen"] = certain_value
        elif var_type in self.need_a_qubit_array:
            final_stmt = "let "+uncertain_value+"QubitArrayLen = "+certain_value+";\n"
            if self.correct:
                self.correct_mid_dict[uncertain_value+"QubitArrayLen"] = certain_value
            else:
                self.wrong_mid_dict[uncertain_value+"QubitArrayLen"] = certain_value
        else:
            return None
        
        return final_stmt

    def generate_correct(self, op: str, certain_value, uncertain_value, relatedArgDict: dict, former_stmt: str):
        """ 根据表达式生成正确的值 """

        final_stmt, complex_stmt = "", ""
        self.correct = True
        # 如果uncertain_value为叶子节点
        if uncertain_value.isLeafNode():
            uncertain_value_name = self.get_var_name(uncertain_value.rootNode)
            uncertain_value_name, var_type = self.process_newtype_attr(uncertain_value_name, relatedArgDict)
        else:
            raise RuntimeError("左节点不是叶子节点！")
        
        # !=则从>或者<中选择一个进行生成
        # print("op:"+op)
        if op == "!=":
            op = random.choice([">", "<"])
        # ==/>=/<=均取=的情况
        if op in ["==", ">=", "<="]:
            final_stmt += self.equal(certain_value, uncertain_value_name, var_type, former_stmt)
        # <取-1/0.1的情况
        elif op == "<":
            final_stmt += self.minus(certain_value, uncertain_value_name, var_type, former_stmt)
        # >取+1/0.1的情况
        elif op == ">":
            final_stmt += self.plus(certain_value, uncertain_value_name, var_type, former_stmt)
        else:
            return None

        return final_stmt

    def generate_wrong(self, op: str, certain_value, uncertain_value, relatedArgDict: dict, former_stmt: str):
        """ 根据表达式生成错误的值"""

        final_stmt = ""
        self.correct = False
        if uncertain_value.isLeafNode():
            uncertain_value_name = self.get_var_name(uncertain_value.rootNode)
            uncertain_value_name, var_type = self.process_newtype_attr(uncertain_value_name, relatedArgDict)
        else:
            raise RuntimeError("左节点不是叶子节点！")
        
        # ==则从>或者<中选择一个进行生成
        if op == "==":
            op = random.choice([">", "<"])
        # !=需要按照给==生成正确值来处理
        if op == "!=":
            final_stmt += self.equal(certain_value, uncertain_value_name, var_type, former_stmt)
        # </<=需要按照给>生成正确值来处理
        elif op in ["<", "<="]:
            final_stmt += self.plus(certain_value, uncertain_value_name, var_type, former_stmt)
        # >/>=需要按照给<生成正确值来处理取-1/0.1的情况
        elif op in [">", ">="]:
            final_stmt += self.minus(certain_value, uncertain_value_name, var_type, former_stmt)
        else:
            return None

        return final_stmt
    
    def generate_complex(self, one_cons_tree: ConstraintTree, relatedArgDict: dict):
        """ 对复杂表达式中的变量进行生成并计算结果 """

        # print("---In generate_complex---")
        complext_stmt = ""
        node_content = one_cons_tree.rootNode
        # print("node_content:"+node_content)
        # 开始对变量进行生成和替换
        tmp_stmt = ""
        regex_for_var = r"([A-Za-z_:]+)"
        for match in re.finditer("Length\(([\w:]+?)\)", node_content):
            real_var = match.group(1)
            # print("real_var:"+real_var)
            arg_name, arg_type = self.process_newtype_attr(real_var, relatedArgDict)
            array_len = assign.generatePosInt()
            tmp_stmt = "let "+arg_name+"ArrayLen = "+array_len+";\n"
            node_content = node_content.replace(match.group(), array_len)
            self.correct_mid_dict[arg_name+"ArrayLen"] = str(array_len)
            self.wrong_mid_dict[arg_name+"ArrayLen"] = str(array_len)
        for match in re.finditer("Length\(([\w:]+?)!?\)", node_content):
            real_var = match.group(1)
            # print("real_var:"+real_var)
            arg_name, arg_type = self.process_newtype_attr(real_var, relatedArgDict)
            array_len = assign.generatePosInt()
            tmp_stmt = "let "+arg_name+"QubitArrayLen = "+array_len+";\n"
            node_content = node_content.replace(match.group(), array_len)
            self.correct_mid_dict[arg_name+"QubitArrayLen"] = str(array_len)
            self.wrong_mid_dict[arg_name+"QubitArrayLen"] = str(array_len)
        for match in re.finditer(regex_for_var, node_content):
            real_var = match.group(1)
            if real_var in ["L", "x", "FFFFFFFFFFFFFFEL", "FFFFFFFFFFFFFFF", "Length"]:
                continue
            # print("real_var:"+real_var)
            arg_name, arg_type = self.process_newtype_attr(real_var, relatedArgDict)
            value = assign.generate_a_param(arg_name, arg_type)
            tmp_stmt = self.generate_declaration(arg_name, arg_type, value)
            node_content = node_content.replace(match.group(), value)
            self.defined_var_dict[arg_name] = DefinedVar(real_var, arg_type, 0, value)
        complext_stmt += tmp_stmt
        new_cons_tree = ConstraintTree(calculate_math_expr(node_content))
        # print("---Out generate_complex---")
        # print("check complex:\n"+complext_stmt)

        return new_cons_tree, complext_stmt
    
    def cover_defined_var(self, expr: str):
        """ 查找是否存在Length(var!)、Length(var)或者var，如果有的话，将其替换成值/长度 """

        # print("check expr:"+expr)
        if "?" in expr:
            return expr, True
        for real_var_name, var_info in self.defined_var_dict.items():
            # print("check covered defined:"+real_var_name+" "+var_info.var_value+" "+str(var_info.var_size))
            if "Length("+real_var_name+"!)" in expr:
                expr = expr.replace("Length("+real_var_name+"!)", str(var_info.var_size))
            elif "Length("+real_var_name+")" in expr:
                expr = expr.replace("Length("+real_var_name+")", str(var_info.var_size))
            elif real_var_name+"::" not in expr and "::"+real_var_name not in expr:
                expr = re.sub(r"\b"+real_var_name+r"\b", var_info.var_value, expr)
                # expr = self.var_to_value(expr, real_var_name, var_info.var_value)
        # print(">>>expr:"+expr)
        for var_name, var_value in self.correct_mid_dict.items():
            # print("check covered mid:"+var_name+" "+var_value)
            var_name = var_name.replace("QubitArrayLen", "").replace("ArrayLen", "")
            if "Length("+var_name+"!)" in expr:
                expr = expr.replace("Length("+var_name+"!)", var_value)
            elif "Length("+var_name+")" in expr:
                expr = expr.replace("Length("+var_name+")", var_value)
        # print("after cover:"+expr)
        try:
            expr = calculate_math_expr(expr)
            return expr, True
        except:
            print("Still has undefined var.")
        return expr, False
    
    def refresh_node_content(self, one_cons_tree: ConstraintTree):
        """ 使用defined_var_dict覆盖已生成变量 """

        # print("---In refresh_node_content---")
        if not (one_cons_tree.leftNode or one_cons_tree.rightNode):
            # print("---No need refresh---")
            return one_cons_tree
        # print(">>>0expr:"+one_cons_tree.leftNode.rootNode)
        expr, all_covered = self.cover_defined_var(one_cons_tree.leftNode.rootNode)
        # print(">>>1expr:"+expr)
        if all_covered:
            one_cons_tree.setNode(ConstraintTree(expr), True, "left")
        else:
            one_cons_tree.setNode(ConstraintTree(expr), False, "left")
        # print(">>>2expr:"+one_cons_tree.rightNode.rootNode)
        expr, all_covered = self.cover_defined_var(one_cons_tree.rightNode.rootNode)
        # print(">>>3expr:"+expr)
        if all_covered:
            one_cons_tree.setNode(ConstraintTree(expr), True, "right")
        else:
            one_cons_tree.setNode(ConstraintTree(expr), False, "right")
        # print("---Out refresh_node_content---")
        return one_cons_tree

    def change_op(self, op: str):
        """ 对两种情况的操作符进行逆转 """

        change_dict = {"+": "-", "-": "+", "/": "*", "*": "/", ">>>": "<<<", "<<<": ">>>", "==": "==", "!=": "!="}
        # print("check op:"+op+".")
        # 当左节点为确定值，右节点为变化值时，需要将顺序进行转换才能按照统一的逻辑生成正确-错误值
        if ">" in op:
            op = re.sub(">", "<", op)
        elif "<" in op:
            op = re.sub("<", ">", op)
        # 将部分项从左式移到右式时，操作符需要改变
        else:
            op = change_dict[op.strip()]

        return op

    def generate_last(self, correct_stmt, wrong_stmt, relatedArgDict):
        """ 生成newtype的最终声明语句 """

        generate_last_args = get_undefined_args(relatedArgDict, self.defined_var_dict)
        # print("generate_last_args:", generate_last_args)
        # 部分变量在correct_mid_dict中存在，但不在wrong_mid_dict中
        for key, value in self.correct_mid_dict.items():
            if key not in self.wrong_mid_dict:
                self.wrong_mid_dict[key] = value
        tmp_correct_stmt, self.defined_var_dict = complex_dec_generator(generate_last_args, self.correct_mid_dict, self.defined_var_dict)
        # 2024-01-03 为ApplyObliviousAmplitudeAmplification生成参数时，newtype属性的声明在newtype本身的声明之后
        # correct_stmt = tmp_correct_stmt+correct_stmt
        correct_stmt = correct_stmt+tmp_correct_stmt
        tmp_wrong_stmt, self.defined_var_dict = complex_dec_generator(generate_last_args, self.wrong_mid_dict, self.defined_var_dict)
        # 同上
        # wrong_stmt = tmp_wrong_stmt+wrong_stmt
        wrong_stmt = wrong_stmt+tmp_wrong_stmt
        # print("===correct_stmt:\n"+correct_stmt+"\n===wrong_stmt:\n"+wrong_stmt)

        return correct_stmt, wrong_stmt

    def generate_value_pair(self, one_cons_tree: ConstraintTree, relatedArgDict: dict, only_generate_correct: bool, last_tree: bool):
        """ 返回两个片段，如果only_generate_correct=True则生成两个正确的表达式，否则生成一个正确的和一个错误的 """

        # print("===relatedArgDict:",relatedArgDict)
        if '' in relatedArgDict.keys():
            del relatedArgDict['']
        # print("==start to generate value pair for:")
        # one_cons_tree.printAll()
        correct_stmt, wrong_stmt, complex_stmt = "", "", ""
        # 如果是第二颗往后的树，先刷新一下已生成的变量
        one_cons_tree = self.refresh_node_content(one_cons_tree)
        # 如果左右节点都是固定值（前面的生成操作已经生成了该树中的所有变量）
        if (one_cons_tree.leftIsCertain == True) and (one_cons_tree.rightIsCertain == True):
            if last_tree:
                return self.generate_last(correct_stmt, wrong_stmt, relatedArgDict)
            else:
                return correct_stmt, wrong_stmt
        # 如果左右节点均是变化值，先将一侧变为固定值
        if not (one_cons_tree.leftIsCertain or one_cons_tree.rightIsCertain):
            # 处理特殊情况：IsPermutation(a)
            # if "IsPermutation" in one_cons_tree.rootNode:
            #     tmp_stmt, self.defined_var_dict = generateFuncReturn(one_cons_tree.rootNode, "", self.correct_mid_dict, self.defined_var_dict, True)
            #     correct_stmt += tmp_stmt
            #     if not only_generate_correct:
            #         tmp_stmt, self.defined_var_dict = generateFuncReturn(one_cons_tree.rootNode, "", self.wrong_mid_dict, self.defined_var_dict, False)
            #         wrong_stmt += tmp_stmt
            #     else:
            #         wrong_stmt = correct_stmt
            #     if last_tree:
            #         return self.generate_last(correct_stmt, wrong_stmt, relatedArgDict)
            #     else:
            #         return correct_stmt, wrong_stmt
            # 处理基础情况
            selected_node = one_cons_tree.rightNode
            # 如果是可生成的叶子节点，调用函数进行生成
            if selected_node.isLeafNode() and countOp(selected_node.rootNode) == 0:
                correct_stmt = self.generate_random_value(one_cons_tree, selected_node, relatedArgDict)
                certain_value = one_cons_tree.rightNode.rootNode
                # print("check certain_value if leaf:"+certain_value)
            # 否则需要进一步处理，生成随机值，并更新右节点表达式
            else:
                new_cons_tree, complex_stmt = self.generate_complex(one_cons_tree.rightNode, relatedArgDict)
                one_cons_tree.setRightNode(new_cons_tree, True)
                certain_value = new_cons_tree.rootNode
                correct_stmt = complex_stmt
                # print("check certain_value if not leaf:"+certain_value)
            # print("after generate one:correct_stmt:\n"+correct_stmt+"complex_stmt:\n"+complex_stmt)
            # 检查一下生成是否成功
            if correct_stmt is None or correct_stmt == "":
                return "", ""
            # elif len(complex_stmt) > 0:
            #     wrong_stmt = correct_stmt
            else:
                wrong_stmt = correct_stmt
            # print("--1check wrong_stmt:\n" + wrong_stmt)
        elif one_cons_tree.rightIsCertain:
            certain_value = one_cons_tree.rightNode.rootNode
        elif one_cons_tree.leftIsCertain:
            certain_value = one_cons_tree.leftNode.rootNode
        # print("middle correct_stmt:\n"+correct_stmt+"middle wrong_stmt:\n"+wrong_stmt)
        # print("certain_value:"+certain_value)
        # print("only_generate_correct:",only_generate_correct)
        # print("after generate one:correct_stmt:\n"+correct_stmt+"complex_stmt:\n"+complex_stmt)
        
        # 开始生成正确错误声明语句
        # 如果左节点是变化值，右节点是固定值
        if not one_cons_tree.leftIsCertain and one_cons_tree.rightIsCertain:
            # 处理基础情况
            op = one_cons_tree.rootNode
            selected_node = one_cons_tree.leftNode
            tmp_stmt = self.generate_correct(op, certain_value, one_cons_tree.leftNode, relatedArgDict,
                                                           correct_stmt)
            if tmp_stmt is None or tmp_stmt == "":
                return "", ""
            else:
                # 先生成的应该在前面
                # correct_stmt += tmp_stmt
                # print("tmp_stmt:"+tmp_stmt)
                correct_stmt = tmp_stmt+correct_stmt
            # 如果需要生成正确和错误值，再调用wrong_stmt将错误片段补充完整
            if not only_generate_correct:
                wrong_stmt += self.generate_wrong(op, certain_value, one_cons_tree.leftNode, relatedArgDict, wrong_stmt)
                # print("--2check wrong_stmt:\n" + wrong_stmt)
            # 否则，correct_stmt和wrong_stmt内容一致
            else:
                wrong_stmt = correct_stmt
        # 如果右节点是变化值，左节点是固定值
        elif one_cons_tree.leftIsCertain and not one_cons_tree.rightIsCertain:
            # print("left is certain:"+one_cons_tree.rightNode.rootNode)
            op = self.change_op(one_cons_tree.rootNode)
            selected_node = one_cons_tree.rightNode
            tmp_stmt = self.generate_correct(op, certain_value, one_cons_tree.rightNode, relatedArgDict, 
                                                           correct_stmt)
            if tmp_stmt is None or tmp_stmt == "":
                return "", ""
            else:
                correct_stmt += tmp_stmt
            if not only_generate_correct:
                wrong_stmt += self.generate_wrong(op, one_cons_tree.leftNode.rootNode, one_cons_tree.rightNode,
                                                 relatedArgDict, wrong_stmt)
            else:
                wrong_stmt = correct_stmt
        else:
            return None, None
        # print("last correct_stmt:\n"+correct_stmt+"last wrong_stmt:\n"+wrong_stmt)
        
        # 根据last_tree值判断是否声明未声明的变量
        # print("value of last tree:"+str(last_tree))
        if last_tree:
            return self.generate_last(correct_stmt, wrong_stmt, relatedArgDict)
        else:
            return correct_stmt, wrong_stmt

if __name__ == "__main__":
    handler = GenerateCorrectAndWrong()
    # 测试表达式Length(targetRegister)>Length(sourceRegister)
    one_cons_tree = ConstraintTree(">")
    one_cons_tree.setLeftNode(ConstraintTree("Length(targetRegister)"), False)
    one_cons_tree.setRightNode(ConstraintTree("Length(sourceRegister)"), False)
    final_stmt = handler.generate_value_pair(one_cons_tree, {'sourceRegister': 'Qubit[]', 'targetRegister': 'Qubit[]'}, False, True)
    """
    # 测试表达式Length(phases::AboutStart) == Length(phases::AboutTarget)
    one_cons_tree = ConstraintTree("==")
    one_cons_tree.setLeftNode(ConstraintTree("Length(phases::AboutStart)"), False)
    # right_node = ConstraintTree("+")
    # right_node.setLeftNode("Length(phases::AboutTarget)", False)
    # right_node.setRightNode("1", True)
    one_cons_tree.setRightNode(ConstraintTree("Length(phases::AboutTarget)+1"), False)
    final_stmt = handler.generate_value_pair(one_cons_tree, {'phases': 'ReflectionPhases'}, False, True)
    # 测试表达式Length(controls) >= 2
    one_cons_tree = ConstraintTree(">=")
    one_cons_tree.setLeftNode(ConstraintTree("Length(controls)"), False)
    one_cons_tree.setRightNode(ConstraintTree("2"), True)
    final_stmt = handler.generate_value_pair(one_cons_tree, {'controls': 'Qubit[]'}, False, True)
    # 测试表达式number <= bits < 63 ? 1 <<< bits | 0x7FFFFFFFFFFFFFFF
    one_cons_tree = ConstraintTree("<=")
    one_cons_tree.setLeftNode(ConstraintTree("number"), False)
    one_cons_tree.setRightNode(ConstraintTree("bits < 63 ? 1 <<< bits | 0x7FFFFFFFFFFFFFFF"), False)
    final_stmt = handler.generate_value_pair(one_cons_tree, {'number': 'Int', 'bits': 'Int'}, False, True)
    """
    print("===final_stmt:\n"+final_stmt[0]+"\n"+final_stmt[1])
   