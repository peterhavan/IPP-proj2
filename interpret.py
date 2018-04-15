
import xml.etree.ElementTree as ET
import argparse
import re
import sys

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
    try:
        tree = ET.parse(filename)
    except (FileNotFoundError, ET.ParseError) as err:
        print(err, file=sys.stdout)
        sys.exit(31)
    root = tree.getroot()
    instList = list()
    frameStack = variableTable()     
    
    for instructionXML in root:
           # print(instructionXML.tag, instructionXML.attrib)
            instList.append(getInst(instructionXML, frameStack))
            #for argumentXML in instructionXML:
            #   print(argumentXML.text, argumentXML.attrib)
           # print("--------")
        
    interpret(frameStack, instList)
            
def getInst(instructionXML, frameStack):
    global order
    argList = list()
    global labelDict
    for argumentXML in instructionXML:
        argList.append([argumentXML.text, list(argumentXML.attrib.values())[0]])
    opcode = instructionXML.attrib.get("opcode")
    if order != int(instructionXML.attrib.get("order")):
        sys.exit(31)
    #order += 1
    opcode = opcode.upper()
     
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
                sys.exit(32)
            
        elif i[1] == "int":
            i[0] = int(i[0])
            
        elif i[1] == "string":
            i[0] = checkStringConst(i[0])
            
            
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
            sys.exit(32)
            
   # elif instruction.name == "MOVE":
        
        
            
def checkVariableName(name):
    if re.match(r'^(GF|LF|TF)@[a-zA-Z_\-\$&%\*]+[a-zA-Z_\-\$&%\*0-9]*$', name):
        return True
    else:
        return False
    
def checkStringConst(const):
    if re.match(r'^[^#\s]*$', const):
#        esc = re.findall(r'\\[0-9]{3}', const)
#        print(esc, "************")
#        for i in esc:
#            re.sub(i, chr(int(i[1:3])), const)
        esc = re.split("\\\\", const)
        result = str()
        for i in esc:
            try:
                int(i[0:2])
#                result += i.replace(i[0:2], chr(int(i[0:2]), 1)
                result += i.replace(i[0:3], chr(int(i[0:3])), 1)
            except ValueError:
                result += i
        return result
    else:
        sys.exit(32)
    
def checkBoolConst(const):
    if re.match(r'^[true|false]+$', const):
        return True
    else:
        return False
    
def checkIntConst(const):
    if re.match(r'^[\+-]?[0-9]+$', const):
        return True
    else:
        return False
    

    
def interpret(frameStack, instList):
    #for instruction in instList:
    #for i in range(len(instList)):
    retList = list()
    global labelDict
    i = 0
    try:
        while i < len(instList):
            instruction = instList[i]
            if instruction.name == "DEFVAR":
                frameStack.addVariable(instruction.args[0])
                
            elif instruction.name == "MOVE":
                frameStack.initVariable(instruction.args[0], instruction.args[1])
                
            elif instruction.name == "CREATEFRAME":
                frameStack.TF = Frame(True)
            
            elif instruction.name == "PUSHFRAME":
                if not frameStack.TF.defined:
                    sys.exit(55)
                frameStack.LF.append(frameStack.TF)
                frameStack.TF.defined = False
                
            elif instruction.name == "POPFRAME":
                if not frameStack.LF:
                    sys.exit(55)
                frameStack.TF = frameStack.LF.pop()
                frameStack.TF.defined = True
                
            elif instruction.name == "WRITE":
                if instruction.args[0][1] == "var":
                    print(frameStack.checkVariableSem(instruction.args[0][0]))
                else:
                    print(instruction.args[0][0])
                
            elif instruction.name == "ADD" \
                or instruction.name == "SUB" \
                or instruction.name == "IDIV" \
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
                frameStack.doNot(instruction.args[0], instruction.args[1])
                
            elif instruction.name == "CONCAT":
                frameStack.doConcat(instruction.args[0], instruction.args[1], instruction.args[2])
                
            elif instruction.name == "JUMP":
                if instruction.args[0][0] in labelDict.keys():
                    i = labelDict.get(instruction.args[0][0])
                else:
                    sys.exit(52)
                    
            elif instruction.name == "CALL":
                if instruction.args[0][0] in labelDict.keys():
                    i = labelDict.get(instruction.args[0][0])
                    retList.append(i)
                else:
                    sys.exit(52)
                    
            elif instruction.name == "RETURN":
                if not retList:
                    sys.exit(56)
                else:
                    i = retList.pop()
                    
            elif instruction.name == "INT2CHAR":
                frameStack.doIntToChar(instruction.args[0], instruction.args[1])
                
            elif instruction.name == "STRI2INT":
                frameStack.doStrToInt(instruction.args[0], instruction.args[1], instruction.args[2])
                    
            elif instruction.name == "JUMPIFEQ"\
                or instruction.name == "JUMPIFNEQ":\
                i = frameStack.doConJump(instruction.name, instruction.args[0], instruction.args[1], instruction.args[2], i)
                
            elif instruction.name == "PUSHS":
                frameStack.doPush(instruction.args[0])
                
            elif instruction.name == "READ":
                frameStack.doRead(instruction.args[0], instruction.args[1])
                
            elif instruction.name == "STRLEN":
                frameStack.doStrLen(instruction.args[0], instruction.args[1])
                
            elif instruction.name == "GETCHAR":
                frameStack.doGetChar(instruction.args[0], instruction.args[1], instruction.args[2])
                    
            elif instruction.name == "SETCHAR":
                frameStack.doSetChar(instruction.args[0], instruction.args[1], instruction.args[2])
                    
            elif instruction.name == "TYPE":
                frameStack.doType(instruction.args[0], instruction.args[1])
                
            elif instruction.name == "BREAK"\
                or instruction.name == "DPRINT":
                    pass
                
            i+=1
    except IndexError:
        sys.exit(32)
        
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
                sys.exit(55)
            else:
                self.LF[-1].variables.update({argName.split('@',1)[1] : "not init"})
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
                sys.exit(54)
            else:
                return self.GF.variables.get(variableName)
            
        elif frameName == "LF":
            if not self.LF:
                sys.exit(55)
            elif variableName not in self.LF[-1].variables.keys():
                sys.exit(54)
            else:
                return self.GF.variables.get(variableName)
                
        elif frameName == "TF":
            if not self.TF.defined:
                sys.exit(55)
            elif variableName not in self.TF.variables.keys():
                sys.exit(54)
            else:
                return self.GF.variables.get(variableName)
        else:
            sys.exit(32)
    
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
            sys.exit(53)
   #     if not self.isSymb(op2) == 'int' and not self.isSymb(op2) == 'var':
   #         sys.exit(53)
   #     if not self.isSymb(op3) == 'int' and not self.isSymb(op3) == 'var':
   #         sys.exit(53)
        result = str()            
        
        if self.isSymb(op2) == 'var':
            a = int(self.checkVariableSem(op2[0]))
        elif self.isSymb(op2) == 'int':
            a = int(op2[0])
        else:
            sys.exit(53)
            
        if self.isSymb(op3) == 'var':
            b = int(self.checkVariableSem(op3[0]))
        elif self.isSymb(op3) == 'int':
            b = int(op3[0])
        else:
            sys.exit(53)
    
        if action == 'ADD':
            result = a + b
            
        elif action == 'SUB':
            result = a - b
        
        elif action == 'IDIV':
            if b == 0:
                sys.exit(57)
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
    #        sys.exit(32)
            
    def doRelation(self, action, op1, op2, op3):
        if not self.isVar(op1):
            sys.exit(54)
        result = str()    
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
            if type(a) == str:
                aType = "string"
            elif type(a) == int:
                aType = "int"
            elif type(a) == bool:
                aType = "bool"
            else:
                sys.exit(52)
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
                sys.exit(52)
        else:
            b = op3[0]
            bType = op3[1]
            
        if bType != aType:
            sys.exit(53)
            
        if action == "LT":
            result = (a < b)
        elif action == "GT":
            result = (a > b)
        elif action == "EQ":
            result = (a == b)
            
        self.update(op1, result)
        
    def doLogic(self, action, op1, op2, op3):
        if not self.isVar(op1):
            sys.exit(54)
        result = str()    
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
        elif self.isSymb(op2) == 'bool':
            a = op2[0]
        else:
            sys.exit(53)
            
        if self.isSymb(op3) == 'var':
            b = self.checkVariableSem(op3[0])
        elif self.isSymb(op3) == 'bool':
            b = op3[0]
        else:
            sys.exit(53)
            
        if action == "AND":
            result = (a and b)
        elif action == "OR":
            result = (a or b)
            
        self.update(op1, result)
        
    def doNot(self, op1, op2):
        if not self.isVar(op1):
            sys.exit(54)
            
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
        elif self.isSymb(op2) == 'bool':
            a = op2[0]
        else:
            sys.exit(53)
            
        result = not a
        
        self.update(op1, result)
        
    def doConcat(self, op1, op2, op3):
        if not self.isVar(op1):
            sys.exit(54)
        result = str()
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
        elif self.isSymb(op2) == 'string':
            a = op2[0]
        else:
            sys.exit(53)
            
        if self.isSymb(op3) == 'var':
            b = self.checkVariableSem(op3[0])
        elif self.isSymb(op3) == 'string':
            b = op3[0]
        else:
            sys.exit(53)
            
        if type(a) != str or type(b) != str:
            sys.exit(53)
            
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
            sys.exit(32)
            
    
        
    def doConJump(self, action, op1, op2, op3, index):
        global labelDict
        
        if op1[0] in labelDict.keys():
            i = labelDict.get(op1[0])
        else:
            sys.exit(52)
            
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
            if type(a) == str:
                aType = "string"
            elif type(a) == int:
                aType = "int"
            elif type(a) == bool:
                aType = "bool"
            else:
                sys.exit(52)
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
                sys.exit(52)
        else:
            b = op3[0]
            bType = op3[1]
            
        if bType != aType:
            sys.exit(53)
            
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
        self.dataStack.append(a)
        
    def doPop(self, op1):
        if not self.isVar(op1):
            sys.exit(53)
        if not self.dataStack():
            sys.exit(56)
        self.update(op1, self.dataStack.pop())
        
    def doIntToChar(self, op1, op2):
        if not self.isVar(op1):
            sys.exit(54)
        result = str()
        if self.isSymb(op2) == 'var':
            b = self.checkVariableSem(op2[0])
            if type(b) != int:
                sys.exit(53)
        
        elif self.isSymb(op2) == 'int':
            b = op2[0]
        
        try:
            result = chr(b)
        except (ValueError, TypeError) as err:
            sys.exit(58)
            
        self.update(op1, result)
            
    def doStrToInt(self, op1, op2, op3):
        if not self.isVar(op1):
            sys.exit(54)
        result = str()
        if self.isSymb(op2) == 'var':
            a = self.checkVariableSem(op2[0])
            if type(a) != str:
                sys.exit(52)
        elif self.isSymb(op2) == 'string':
            a = op2[0]
        else:
            sys.exit(53)
            
        if self.isSymb(op3) == 'var':
            b = self.checkVariableSem(op3[0])
            if type(a) != int:
                sys.exit(52)
        elif self.isSymb(op3) == 'int':
            b = op2[0]  
        else:
            sys.exit(53)
        
        try:
            result = ord(a[b])
        except (TypeError, IndexError) as err:
            sys.exit(58)
            
        self.update(op1, result)
        
    def doRead(self, op1, op2):
        if not self.isVar(op1):
            sys.exit(54)
        result = str()            
        if op2[1] != 'type':
            sys.exit(32)
            
        if op2[0] == 'string':
            result = input()
            result = checkStringConst(result)
        
        elif op2[0] == 'bool':
            result = input()
            if result.lower() == 'true':
                result = True
            else:
                result = False
            
        elif op2[0] == 'int':
            result = input()
            try:
                result = int(result)
            except (ValueError, TypeError) as err:
                result = 0
            
        else:
            sys.exit(32)
            
        self.update(op1, result)
        
    def doStrLen(self, op1, op2):
        if not self.isVar(op1):
            sys.exit(54)
        result = str()            
        if op2[1] == 'string':            
            a = op2[0]
            
        elif op2[1] =='var':
            a = self.checkVariableSem(op2[0])
            if type(a) != 'str':
                sys.exit(53)
        else:
            sys.exit(32)
            
        result = len(a)
        
        self.update(op1, result)
        
    
    def doGetChar(self, op1, op2, op3):
        if not self.isVar(op1):
            sys.exit(54)
        result = str()
        if op2[1] == 'string':            
            a = op2[0]
            
        elif op2[1] =='var':
            a = self.checkVariableSem(op2[0])
            if type(a) != 'string':
                sys.exit(53)
        else:
            sys.exit(32)
            
        if op3[1] == 'int':            
            b = op3[0]
            
        elif op3[1] =='var':
            b = self.checkVariableSem(op3[0])
            if type(b) != 'int':
                sys.exit(53)
        else:
            sys.exit(32)
            
            
        try:
            result = a[b]
        except IndexError:
            sys.exit(58)
        
        self.update(op1, result)
            
        
    def doSetChar(self, op1, op2, op3):
        if not self.isVar(op1):
            sys.exit(54)
	            
        result = str()
        if op2[1] == 'int':            
            a = op2[0]
            
        elif op2[1] =='var':
            a = self.checkVariableSem(op2[0])
            if type(a) != 'int':
                sys.exit(53)
        else:
            sys.exit(32)
            
        if op3[1] == 'string':            
            b = op3[0]
            
        elif op3[1] =='var':
            b = self.checkVariableSem(op3[0])
            if type(b) != 'string':
                sys.exit(53)
        else:
            sys.exit(32)
            
            
        try:
            result = self.checkVariableSem(op1[0])
            tmp = list()
            for i in b:
                tmp.append(i)
            tmp[a] = b[0]
            
            result = ''.join(tmp)
        except IndexError:
            sys.exit(58)
        
        self.update(op1, result)
        
    def doType(self, op1, op2):
        if not self.isVar(op1):
            sys.exit(54)
	    
        result = str()
        if op2[1] =='var':
            a = self.checkVariableSem(op2[0])
            if type(a) == 'int':
                result = 'int'
            elif type(a) == 'string':
                result = 'string'
            elif type(a) == 'bool':
                result = 'bool'
        else:
            result = op2[1]
            
        self.update(op1, result)
        
                
    #def 
            
            
        
                   
class Instruction:
    def __init__(self, name, args):
        self.name = name
        self.args = args
       # self.counter += 1
       # print(self.counter)
        

    
    
if __name__ == '__main__':
    main()
    
