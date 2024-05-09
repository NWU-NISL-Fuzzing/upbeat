# -*- coding: utf-8 -*-

import re
import math
import random
# import json

from six import unichr

from grammar_pattern.APIOperator import APIOperator
from grammar_pattern.selfDefinedOpLoad import OperationLoad


endian_type_list = ['LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'LogicalRegister']
complex_type_list = ['Complex','ComplexPolar']
new_type_list = ['LittleEndian', 'BigEndian', 'PhaseLittleEndian', 'SignedLittleEndian', 'LogicalRegister', 
                'Complex', 'ComplexPolar', 'FixedPoint', 
                'GeneratorIndex', 'RotationPhases', 'ReflectionPhases', 'SingleQubitClifford', 
                'Fraction', 'BigFraction', 'CCNOTop', 'SamplingSchedule', 'TrainingOptions',
                'LabeledSample', 'GeneratorSystem', 'SequentialModel','ControlledRotation',
                'ReflectionOracle', 'ObliviousOracle', 'HTerm']
generic_to_concrete = ["Int", "BigInt", "Double", "Pauli", "Bool", "Range"]

standard_api_list = APIOperator().init_api_list()

class Assignment:
    def __init__(self, params):
        self.type_mapping = {
            'PositiveInt': self.generatePosInt,
            'Int': self.generateInteger,
            'BigInt': self.generateBigInt,
            'Bool': self.generateBoolean,
            'String': self.generateString,
            'Result': self.generateResult,
            'Double': self.generateDouble,
            'Qubit': self.generateQubit,
            'Pauli': self.generatePauli,
            'BoundaryInt': self.generateBoundaryInteger,
            'BoundaryDouble': self.generateBoundaryDouble,
            'BoundaryBigInt': self.generateBoundaryBigInt,
            'Range': self.generateRange
        }
        self.params = params
        self.needful_namespace = ""
        self.defined_call = []
        self.unit_type = ["Unit  is Adj", "Unit  is Ctl", "Unit  is Adj + Ctl"]
    
    def find_from_self_def(self, input_str, output_str, func_type):
        """ 从selfDefinedOperations.txt中查找可以使用的API """

        opLoad = OperationLoad()
        selfDefinedFunctions, selfDefinedOperations = opLoad.loadCallables(self.params["work_dir"]+"/Generate/data/selfDefinedOperations.txt")
        func_name = ""
        input_list = input_str[2:-2].split(",")
        if output_str == "Unit":
            output_str = random.choice(self.unit_type).replace("  ", " ")
        # print("check in find_from_self_def:"+str(input_list)+" "+output_str)
        if func_type == "function":
            for i in selfDefinedFunctions:
                if i.argTypes == input_list and i.returnType == output_str:
                    # print(i.content)
                    self.defined_call.append(i)
                    func_name = i.name
                    break
            if len(self.defined_call) > 0:
                return func_name
        else:
            for i in selfDefinedOperations:
                if i.argTypes == input_list and i.returnType == output_str:
                    # print(i.content)
                    self.defined_call.append(i)
                    func_name = i.name
                    break
            if len(self.defined_call) > 0:
                return func_name
        return None
    
    def find_from_doc(self, input_str, output_str):
        """ 从标准文档中查找可以使用的API """

        # 在json文件中查找
        res = [item for item in standard_api_list if str(item.requireTypes) == input_str and item.returnType == output_str]
        # 如果存在多个匹配项，随机选择一个
        if len(res) > 0:
            r = random.choice(res)
            self.needful_namespace += "open "+r.namespace+";\n"
            # print("needful_namespace:\n"+self.needful_namespace)
            return r.name
        else:
            return None

    def generateAPIName(self, var_type:str):
        """ 根据参数类型和返回类型获取合适的API """

        local_generic_to_concrete = []
        unit_dict = {"Unit is Adj":"Unit  is Adj", "Unit is Ctl":"Unit  is Ctl", "Unit is Adj + Ctl":"Unit  is Adj + Ctl"}
        # 获取API的输入和输出
        if var_type.startswith("(") and var_type.endswith(")"):
            var_type = var_type[1:-1]
        # TODO.有可能->和=>同时存在
        if "->" in var_type:
            tmp = re.split("->| -> ", var_type)
            func_type = "function"
        else:
            tmp = re.split("=>| => ", var_type)
            func_type = "operation"
        # 获取输入
        input_str = "['"
        input_list = tmp[0].split(",")
        for i in input_list:
            # print("i:"+i)
            if "'" in i:
                if "=>" in var_type:
                    tmp_type = "Qubit"
                else:
                    tmp_type = random.choice(generic_to_concrete)
                input_str += tmp_type+","
                local_generic_to_concrete.append(tmp_type)
            else:
                input_str += i+","
        input_str = input_str[:-1] + "']"
        # 获取输出
        if "'" in tmp[1]:
            if len(local_generic_to_concrete) > 0:
                output_str = "'"+random.choice(local_generic_to_concrete)+"'"
            else:
                output_str = "'"+random.choice(generic_to_concrete)+"'"
        elif tmp[1] in unit_dict:
            output_str = unit_dict[tmp[1]]
        else:
            output_str = tmp[1]
        # print("input_str:"+input_str+" output_str:"+output_str)
        api_name = self.find_from_doc(input_str, output_str)
        # 有的返回值为Unit  is Adj可以使用Unit进行查找
        if api_name is None and output_str == "Unit":
            output_str = random.choice(self.unit_type)
            # print("find again:"+input_str+" "+output_str)
            api_name = self.find_from_doc(input_str, output_str)
        # elif api_name is None and output_str in self.unit_type:
        #     output_str = "Unit"
        #     # print("find again:"+input_str+" "+output_str)
        #     api_name = self.find_from_doc(input_str, output_str)
        if not api_name:
            api_name = self.find_from_self_def(input_str, output_str.replace("  ", " "), func_type)
        # print("api_name:"+api_name)
        return api_name
    
    def generateRange(self):
        values = ""
        for i in range(3):
            values += str(random.randint(-10, 10)) + ".."
        if "..0.." in values:
            values = values.replace("..0..", "..1..")
        return values[:-2]
    
    def generateNewType(self, var_name: str, var_type: str):
        if var_type in endian_type_list:
            return var_type+'('+var_name+'QubitArray)'
        elif var_type in complex_type_list:
            return var_type+'('+self.generateSmallDouble()+', '+self.generateSmallDouble()+')'
        elif var_type == 'FixedPoint':
            n = random.choice([0,1,2])
            if n == 0:
                return 'FixedPoint(1, '+var_name+'QubitArray)'
            elif n == 1:
                return 'FixedPoint(2, '+var_name+'QubitArray)'
            else:
                return 'FixedPoint(Length('+var_name+'QubitArray), '+var_name+'QubitArray)'
        elif var_type == 'GeneratorIndex':
            return 'GeneratorIndex(([1, 1, 2], [PI()]), [0, 1, 2])'
        elif var_type == 'RotationPhases':
            return 'RotationPhases('+self.generateArray("Double", 1, var_name)+')'
        elif var_type == 'Fraction':
            return 'Fraction('+self.generateInteger()+","+self.generateInteger()+")"
        elif var_type == 'BigFraction':
            return 'BigFraction('+self.generateBigInt()+","+self.generateBigInt()+")"
        elif var_type == 'CCNOTop':
            n = random.choice([0,1])
            if n == 0:
                return 'CCNOTop(ApplyAnd)'
            else:
                return 'CCNOTop(ApplyLowDepthAnd)'
        elif var_type == 'ReflectionOracle':
            self.needful_namespace += 'open Microsoft.Quantum.Canon;\n'
            return 'ReflectionOracle(RAll0)'
        elif var_type == 'ObliviousOracle':
            self.needful_namespace += 'open Microsoft.Quantum.Canon;\n'
            return 'ObliviousOracle(NoOp)'
        elif var_type == 'SignedLittleEndian':
            return 'SignedLittleEndian(LittleEndian('+var_name+'QubitArray))'
        elif var_type == 'SingleQubitClifford':
            value = 'SingleQubitClifford(('
            for i in range(4):
                value += random.choice(['0', '1'])+", "
            return value[:-2]+'))'
        elif var_type == 'SamplingSchedule':
            return 'SamplingSchedule('+self.generateArray("Range", 1, "")+')'
        elif var_type == 'TrainingOptions':
            return 'TrainingOptions(0.1, 0.005, 15, 10000, 16, 8, 0.01, 1,Ignore<String>)'
        elif var_type == 'LabeledSample':
            return random.choice([  'LabeledSample(([0.581557, 0.562824, 0.447721, 0.380219], 1))',
                                    'LabeledSample(([0.570241, 0.544165, 0.503041, 0.354484], 1))',
                                    'LabeledSample(([0.510784, 0.475476, 0.453884, 0.554087], 0))',
                                    'LabeledSample(([0.492527, 0.473762, 0.471326, 0.557511], 0))'])
        elif var_type == 'GeneratorSystem':
            self.needful_namespace += "open Microsoft.Quantum.Arrays;\n"
            n = random.choice([0,1])
            if n == 0:
                return 'GeneratorSystem(1, LookupFunction([GeneratorIndex(([0],[0.0]),[0])]))'
            else:
                return 'GeneratorSystem(1, LookupFunction([GeneratorIndex(([1],[1.0]),[0])]))'
        elif var_type == 'ReflectionPhases':
            value = 'ReflectionPhases('
            value += self.generateArrayWithFixedSize(self.params, "Double", 1, 5)[0] + ', '
            value += self.generateArrayWithFixedSize(self.params, "Double", 1, 5)[0]
            value += ')'
            return value
        elif var_type == 'ControlledRotation':
            n = random.choice([0, 1])
            if n:
                return "ControlledRotation((2, [0]), PauliX, 0)"
            else:
                return "ControlledRotation((0, [1, 2]), PauliZ, 1)"
        elif var_type == 'SequentialModel':
            return "SequentialModel([ControlledRotation((2, [0]), PauliX, 0),ControlledRotation((0, [1, 2]), PauliZ, 1)],[1.234, 2.345],0.0)"
        elif var_type == 'HTerm':
            float_str = str(random.random())+", "+str(random.random())+", "+str(random.random())
            return "HTerm([0, 1, 2], ["+float_str+"])"
        elif var_type == 'JWOptimizedHTerms':
            return 'JWOptimizedHTerms('+self.generateNewType("", "HTerm")+", "+\
                    self.generateNewType("", "HTerm")+", "+\
                    self.generateNewType("", "HTerm")+", "+\
                    self.generateNewType("", "HTerm")+")"
        elif var_type == 'DiscreteOracle':
            self.defined_call.apend("""operation ApplyTOracle (power : Int, target : Qubit[]) : Unit is Adj + Ctl {
for idxPower in 0 .. power - 1 {
        T(Head(target));
    }
}""")
            return 'DiscreteOracle(ApplyTOracle)'

    def generatePauli(self):
        values = ["PauliI", "PauliX", "PauliY", "PauliZ"]
        return random.choice(values)
    
    def generatePosInt(self, max_value=5):
        return str(random.randint(1, max_value))

    def generateInteger(self):
        power = random.randint(0, 3)
        width = -(math.pow(10, power))
        return str(random.randint(width, -width))

    def generateBoundaryInteger(self):
        boundaries = self.params["boundaryValue"]["Int"]
        num = random.choice(boundaries)
        return str(num)

    def generateBoundaryBigInt(self):
        boundaries = self.params["boundaryValue"]["BigInt"]
        num = random.choice(boundaries)
        return str(num)

    def generateBoundaryDouble(self):
        boundaries = self.params["boundaryValue"]["Double"]
        num = random.choice(boundaries)
        return str(num)

    def generateBigInt(self):
        power = random.randint(0, 3)
        width = -(math.pow(10, power))
        return str(random.randint(width, -width)) + "L"
    
    def generateSmallDouble(self):
        """ Generate decimals between 0 and 1 """

        return str(random.random())

    def generateDouble(self):
        return str(self.generateInteger()) + (str(random.random())[1:])

    def generateString(self):
        length = random.randint(1, 128)
        result = ''
        start, end = (32, 126)
        while length > 0:
            try:
                newChar = unichr(random.randint(start, end))
                if newChar.__eq__('"') or newChar.__eq__('\\'):
                    newChar = '\\' + newChar
                result += newChar
            except UnicodeEncodeError:
                pass
            length -= 1
        result = result.replace('\"', '')
        result = result.replace("'", "")
        result = result.replace('\n', '')
        result = result.replace('\r', '')
        result = result.replace('{', '')
        result = result.replace('}', '')
        result = result.replace('\\', '')
        result = result.replace('/', '')
        return '"' + result + '"'

    def generateBoolean(self):
        return str(bool(random.randint(0, 1))).lower()

    def generateResult(self):
        values = ["Zero", "One"]
        return random.choice(values)

    def generateQubit(self):
        return "Qubit()"

    def generateNewtypeElem(self, time: int, var_name: str, var_type: str):
        values = ""
        for i in range(time):
            values += self.generateNewType(var_name+str(i), var_type ) + ","
        return values[:-1]

    def generateArray(self, type, braceCount, var_name):
        values = ""
        if type in self.type_mapping.keys():
            time = random.randint(1, 2)
            if type.lower() == 'qubit':
                values += "Qubit[" + str(time) + "]"
            else:
                time = random.randint(1, 5)
                if braceCount == 1:
                    for i in range(time):
                        values += str(self.type_mapping[type]()) + ","
                    values = "[" + values[0:-1] + "]"
                elif braceCount == 2:
                    for i in range(time):
                        value = ""
                        for i in range(time):
                            value += str(self.type_mapping[type]()) + ","
                        value = "[" + value[0:-1] + "]"
                        values += value + ","
                    values = "[" + values[0:-1] + "]"
        # newtype类型数组的生成
        elif type in new_type_list:
            if braceCount == 1:
                n = random.randint(1, 2)
                values = "[" + self.generateNewtypeElem(n, var_name, type) + "]"
            elif braceCount == 2:
                values = "[[" + self.generateNewtypeElem(2, var_name, type) + "], [" + self.generateNewtypeElem(2, var_name, type) + "]]"
        # 泛型生成
        elif "'" in type:
            type = random.choice(generic_to_concrete)
            time = random.randint(1, 5)
            for i in range(time):
                value = self.generate_a_param("",  type)
                values += str(value) + ","
            values = "[" + values[0:-1] + "]"
        # 否则赋空数组
        else:
            # values = "new "+type+"[]"
            values = "EmptyArray<"+type+">()"
        return values

    @staticmethod
    def generateArrayWithFixedSize(params, var_type, braceCount, time, var_num=0):
        if time == 0:
            return "EmptyArray<"+var_type+">()", var_num
        assign = Assignment(params)
        values = ""
        # 常规类型数组的生成
        if var_type in assign.type_mapping.keys():
            #ToDo:根据braceCount生成二维qubit数组
            if var_type.lower() == 'qubit':
                    values += "Qubit[" + str(time) + "]"
            else:
                if braceCount == 1:
                    for i in range(time):
                        values += str(assign.type_mapping[var_type]()) + ","
                    values = "[" + values[0:-1] + "]"
                elif braceCount == 2:
                    for i in range(time):
                        value = ""
                        for i in range(time):
                            value += str(assign.type_mapping[var_type]()) + ","
                        value = "[" + value[0:-1] + "]"
                        values += value + ","
                    values = "[" + values[0:-1] + "]"
        # newtype类型数组的生成
        elif var_type in new_type_list:
            for i in range(time):
                values += assign.generateNewType(var_num, var_type) + ","
            values = "[" + values[0:-1] + "]"
        # 泛型生成
        elif "'" in var_type:
            var_type = random.choice(generic_to_concrete)
            for i in range(time):
                value = assign.generate_a_param("", var_type)
                values += str(value) + ","
            values = "[" + values[0:-1] + "]"
        # 否则类型不能生成，赋空数组
        else:
            values = "EmptyArray<"+var_type+">()"
        return values, var_num

    def generate_random_type_param(self):
        type = random.choice(list(self.type_mapping.keys()))
        value = self.type_mapping[type]()
        return value

    def generate_a_param(self, var_name, var_type):
        # print("var_name:"+var_name+" var_type:"+var_type)
        if "=>" in var_type or "->" in var_type:
            value = self.generateAPIName(var_type)
        elif var_type in new_type_list:
            value = self.generateNewType(var_name, var_type)
        elif var_type in self.type_mapping.keys():
            value = self.type_mapping[var_type]()
        else:
            left_brace = var_type.count("[")
            right_brace = var_type.count("]")
            # 一维和二维数组生成
            if left_brace == right_brace == 1:
                var_type = var_type.replace('[', '')
                var_type = var_type.replace(']', '')
                value = self.generateArray(var_type.strip(), 1, var_name)
            elif left_brace == right_brace == 2:
                var_type = var_type.replace('[', '')
                var_type = var_type.replace(']', '')
                value = self.generateArray(var_type.strip(), 2, var_name)
            else:
                value = None
        return value
