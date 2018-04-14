
import xml.etree.ElementTree as ET
import argparse
import re

call = 0
order = 1
labelDict = dict()

def getOptions():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="source file") #required=True
    args = parser.parse_args()
    return args.source
    

def main():
    filename = getOptions()
    tree = ET.parse(filename)
    root = tree.getroot()
    instList = list()
    frameStack = variableTable()     
    
    for instructionXML in root:
           # print(instructionXML.tag, instructionXML.attrib)
            instList.append(getInst(instructionXML, frameStack))
            #for argumentXML in instructionXML:
            #   print(argumentXML.text, argumentXML.attrib)
           # print("--------")
    for i in instList:
        print(i.name)
        print(i.args)
        print("---------")
        
    interpret(frameStack, instList)
            
def getInst(instructionXML, frameStack):
    global order
    argList = list()
    global labelDict
    for argumentXML in instructionXML:
        argList.append([argumentXML.text, list(argumentXML.attrib.values())[0]])
    opcode = instructionXML.attrib.get("opcode")
    if order != int(instructionXML.attrib.get("order")):
        exit(31)
    #order += 1
     
    inst = Instruction(opcode, argList)
    
    if opcode == "LABEL":
            labelDict.update({inst.args[0][0] : order-1})
            
    for i in inst.args:
        if str(i[0]) == "None":
            i[0] = ""
            
        elif i[1] == "bool":
            if i[0] == "false":
                i[0] = False
            elif i[0] == "true":
                i[0] = True
            else:
                exit(32)
            
        elif i[1] == "int":
            i[0] = int(i[0])
            
    order += 1
    checkInst(inst)
    return inst

def checkInst(instruction):
    varSymb = ["MOVE"]
    noOp = ["CREATEFRAME", "POPFRAME", "PUSHFRAME", "RETURN", "BREAK"]
    var = ["DEFVAR", "POPS"]
    label = ["CALL"]
    math = ["ADD", "SUB", "MUL", "IDIV"]
    relation = ["LT", "GT", "EQ"]
    logic = ["AND", "OR"]
    string = ["CONCAT", "GETCHAR", "SETCHAR"]
    conJump = ["JUMPIFEQ", "JUMPIFNEQ"]
    #NOT
    #DPRINT
    #JUMP
    #LABEL
    #TYPE
    #WRITE
    #INT2CHAR
    #REDAD
    #STRI2INT
    if instruction.name in noOp:
        if not instruction.args:
            pass
        else:
            exit(32)
            
   # elif instruction.name == "MOVE":
        
        
            
def checkVariableName(name):
    if re.match(r'^(GF|LF|TF)@[a-zA-Z_\-\$&%\*]+[a-zA-Z_\-\$&%\*0-9]*$', name):
        return True
    else:
        return False
    
def checkStringConst(const):
    if re.match(r'^string@[^#\s]*$', const):
        return True
    else:
        return False
    
def checkBoolConst(const):
    if re.match(r'^bool@[true|false]+$', const):
        return True
    else:
        return False
    
def checkIntConst(const):
    if re.match(r'^int@[\+-]?[0-9]+$', const):
        return True
    else:
        return False
    

    
def interpret(frameStack, instList):
    #for instruction in instList:
    #for i in range(len(instList)):
    global labelDict
    i = 0
    while i < len(instList):
        instruction = instList[i]
        if instruction.name == "DEFVAR":
            frameStack.addVariable(instruction.args[0])
            
        elif instruction.name == "MOVE":
            frameStack.initVariable(instruction.args[0], instruction.args[1])
            
        elif instruction.name == "CREATEFRAME":
            frameStack.TF = Frame(True)
        
        elif instruction.name == "PUSHFRAME":
            frameStack.LF.append(frameStack.TF)
            frameStack.TF.defined = False
            
        elif instruction.name == "POPFRAME":
            if not frameStack.LF:
                exit(55)
            frameStack.TF = frameStack.LF.pop()
            frameStack.TF.defined = True
            
        elif instruction.name == "WRITE":
            if instruction.args[0][1] == "var":
                print(frameStack.checkVariableSem(instruction.args[0][0]))
            else:
                print(instruction.args[0][0])
            
        elif instruction.name == "ADD" \
            or instruction.name == "SUB" \
            or instruction.name == "DIV" \
            or instruction.name == "MUL":\
            frameStack.doMath(instruction.name, instruction.args[0], instruction.args[1], instruction.args[2])
            
        elif instruction.name == "LT" \
            or instruction.name == "GT" \
            or instruction.name == "EQ": \
            frameStack.doRelation(instruction.name, instruction.args[0], instruction.args[1], instruction.args[2])
            
        elif instruction.name == "AND" \
            or instruction.name == "OR": \
            frameStack.doLogic(instruction.name, instruction.args[0], instruction.args[1], instruction.args[2])
            
        elif instruction.name == "NOT":
            frameStack.doLogic(instruction.name, instruction.args[0], instruction.args[1])
            
        elif instruction.name == "CONCAT":
            frameStack.doConcat(instruction.args[0], instruction.args[1], instruction.args[2])
            
        elif instruction.name == "JUMP":
            if instruction.args[0][0] in labelDict.keys():
                i = labelDict.get(instruction.args[0][0])
            else:
                exit(52)
                
        elif instruction.name == "JUMPIFEQ"\
            or instruction.name == "JUMPIFNEQ":\
            i = frameStack.doConJump(instruction.name, instruction.args[0], instruction.args[1], instruction.args[2], i)
            
        elif instruction.name == "PUSHS":
            frameStack.doPush(instruction.args[0])
        
        i+=1
        
class Frame:
    def __init__(self, defined):
        self.variables = dict()
        self.defined = defined
        
   # def addVariable(self, variableName):
    #    self.variables.get(variableName, "not init")
        
class variableTable:
    def __init__(self):
        self.GF = Frame(True)
        self.LF = list()
        self.TF = Frame(False)
        self.dataStack = list()
    
    def addVariable(self, arg):
        argName = arg[0]
        frameName = argName.split('@',1)[0]
        if frameName == "GF":
            self.GF.variables.update({argName.split('@',1)[1] : "not init"})
        elif frameName == "LF":
            if not self.LF:
                exit(55)
            else:
                self.LF[-1].variables.update0({argName.split('@',1)[1] : "not init"})
        elif frameName == "TF":
            self.TF.variables.update({argName.split('@',1)[1] : "not init"})
            
    def initVariable(self, name, op1):
        value = op1[0]
        argName = name[0]
        frameName = argName.split('@',1)[0]
        variableName = argName.split('@',1)[1]
        if str(value) == "None":
            value = str()
        self.checkVariableSem(argName)
        if frameName == "GF":
            self.GF.variables.update({variableName : value})                
        elif frameName == "LF":
             self.LF[-1].variables.update({variableName : value})
                
        elif frameName == "TF":
            self.TF.variables.update({variableName : value})
                
    def checkVariableSem(self, variable):
        frameName = variable.split('@',1)[0]
        variableName = variable.split('@',1)[1]
        if frameName == "GF":
            if variableName not in self.GF.variables.keys():
                exit(54)
            else:
                return self.GF.variables.get(variableName)
            
        elif frameName == "LF":
            if not self.LF:
                exit(55)
            elif variableName not in self.LF[-1].variables.keys():
                exit(54)
            else:
                return self.GF.variables.get(variableName)
                
        elif frameName == "TF":
            if not self.TF.defined:
                exit(55)
            elif variableName not in self.TF.variables.keys():
                exit(54)
            else:
                return self.GF.variables.get(variableName)
        else:
            exit(32)
    
    def isVar(self, variable):
        if variable[1] != 'var':
            return False
        
        self.checkVariableSem(variable[0])
        return True
    
    def isSymb(self, symb):
        if self.isVar(symb):
            return 'var'
        
        if symb[1] == 'string':
            return 'string'
        
        elif symb[1] == 'bool':
            return 'bool'    
        
        elif symb[1] == 'int':
            return 'int'
        
            
    def doMath(self, action, op1, op2, op3):
        if not self.isVar(op1):
            exit(53)
   #     if not self.isSymb(op2) == 'int' and not self.isSymb(op2) == 'var':
   #         exit(53)
   #     if not self.isSymb(op3) == 'int' and not self.isSymb(op3) == 'var':
   #         exit(53)
            
        
        if self.isSymb(op2) == 'var':
            a = int(self.checkVariableSem(op2[0]))
        elif self.isSymb(op2) == 'int':
            a = int(op2[0])
        else:
            exit(53)
            
        if self.isSymb(op3) == 'var':
            b = int(self.checkVariableSem(op3[0]))
        elif self.isSymb(op3) == 'int':
            b = int(op3[0])
        else:
            exit(53)
    
        if action == 'ADD':
            result = a + b
            
        elif action == 'SUB':
            result = a - b
        
        elif action == 'IDIV':
            if b == 0:
                exit(57)
            result = int(a // b)
        
        elif action == 'MUL':
            result = a * b
            
        self.update(op1, result)
        
    #    frameName = op1[0].split('@',1)[0]
    #    variableName = op1[0].split('@',1)[1]
        
    #    if frameName == "GF":
    #        self.GF.variables.update({variableName : result})
            
    #    elif frameName == "LF":
    #        self.LF[-1].variables.update({variableName : result})
                
    #    elif frameName == "TF":
    #        self.TF.variables.update({variableName : result})
    #    else:
    #        exit(32)
            
    def doRelation(self, action, op1, op2, op3):
        if not self.isVar(op1):
            exit(53)
            
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
            if type(a) == str:
                aType = "string"
            elif type(a) == int:
                aType = "int"
            elif type(a) == bool:
                aType = "bool"
            else:
                exit(52)
        else:
            a = op2[0]
            aType = op2[1]
            
        if self.isSymb(op3) == 'var':
            b = self.checkVariableSem(op3[0])
            if type(b) == str:
                bType = "string"
            elif type(b) == int:
                bType = "int"
            elif type(b) == bool:
                bType = "bool"
            else:
                exit(52)
        else:
            b = op3[0]
            bType = op3[1]
            
        if bType != aType:
            exit(53)
            
        if action == "LT":
            result = (a < b)
        elif action == "GT":
            result = (a > b)
        elif action == "EQ":
            result = (a == b)
            
        self.update(op1, result)
        
    def doLogic(self, action, op1, op2, op3):
        if not self.isVar(op1):
            exit(53)
            
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
        elif self.isSymb(op2) == 'bool':
            a = op2[0]
        else:
            exit(53)
            
        if self.isSymb(op3) == 'var':
            b = self.checkVariableSem(op3[0])
        elif self.isSymb(op3) == 'bool':
            b = op3[0]
        else:
            exit(53)
            
        if action == "AND":
            result = (a and b)
        elif action == "OR":
            result = (a or b)
            
        self.update(op1, result)
        
    def doNot(self, op1, op2):
        if not self.isVar(op1):
            exit(53)
            
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
        elif self.isSymb(op2) == 'bool':
            a = op2[0]
        else:
            exit(53)
            
        result = not a
        
        self.update(op1, result)
        
    def doConcat(self, op1, op2, op3):
        if not self.isVar(op1):
            exit(53)
        
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
        elif self.isSymb(op2) == 'string':
            a = op2[0]
        else:
            exit(53)
            
        if self.isSymb(op3) == 'var':
            b = self.checkVariableSem(op3[0])
        elif self.isSymb(op3) == 'string':
            b = op3[0]
        else:
            exit(53)
            
        if type(a) != str or type(b) != str:
            exit(53)
            
        result = (a + b)
    
        self.update(op1, result)            
        
        
            
    def update(self, op1, result):
        frameName = op1[0].split('@',1)[0]
        variableName = op1[0].split('@',1)[1]
        
        if frameName == "GF":
            self.GF.variables.update({variableName : result})
            
        elif frameName == "LF":
            self.LF[-1].variables.update({variableName : result})
                
        elif frameName == "TF":
            self.TF.variables.update({variableName : result})
        else:
            exit(32)
            
    
        
    def doConJump(self, action, op1, op2, op3, index):
        global labelDict
        
        if op1[0] in labelDict.keys():
            i = labelDict.get(op1[0])
        else:
            exit(52)
            
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
            if type(a) == str:
                aType = "string"
            elif type(a) == int:
                aType = "int"
            elif type(a) == bool:
                aType = "bool"
            else:
                exit(52)
        else:
            a = op2[0]
            aType = op2[1]
            
        if self.isSymb(op3) == 'var':
            b = self.checkVariableSem(op3[0])
            if type(b) == str:
                bType = "string"
            elif type(b) == int:
                bType = "int"
            elif type(b) == bool:
                bType = "bool"
            exit(52)
        else:
            b = op3[0]
            bType = op3[1]
            
        if bType != aType:
            exit(53)
            
        if action == "JUMPIFEQ":
            result = (a == b)
        elif action == "JUMPIFNEQ":
            result = (a != b)
            
        if result:
            index = i
            
        return index
    
    def doPush(self, op1):
        if self.isSymb(op1) == 'var':
            a = self.checkVariableSem(op1[0])
        else:
            a = op1[0]
        self.dataStack.apped(a)
        
    def doPop(self, op1):
        if not self.isVar(op1):
            exit(53)
        if not self.dataStack():
            exit(56)
            
        
        self.update(op1, self.dataStack.pop())
        
        
        
        
                
    #def 
            
            
        
                   
class Instruction:
    def __init__(self, name, args):
        self.name = name
        self.args = args
       # self.counter += 1
       # print(self.counter)
        

    
    
if __name__ == '__main__':
    main()
    
