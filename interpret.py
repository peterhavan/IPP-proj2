
import xml.etree.ElementTree as ET
import argparse

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
    argList = list()
    for argumentXML in instructionXML:
        argList.append((argumentXML.text, list(argumentXML.attrib.values())[0]))
    opcode = instructionXML.attrib.get("opcode")
    
    inst = Instruction(opcode, argList)
    return inst
    
def interpret(frameStack, instList):
    for instruction in instList:
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
                print(frameStack.checkVariable(instruction.args[0][0]))
            else:
                print(instruction.args[0][0])
            
        elif instruction.name == "ADD"
        
        
    
    
        
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
    
    def addVariable(self, arg):
        argName = arg[0]
        frameName = argName.split('@',1)[0]
        if frameName == "GF":
            self.GF.variables.get(argName.split('@',1)[1], "not init")
        elif frameName == "LF":
            if not self.LF:
                exit(55)
            else:
                self.LF.variables.get(argName.split('@',1)[1], "not init")
        elif frameName == "TF":
            self.TF.variables.get(argName.split('@',1)[1], "not init")
            
    def initVariable(self, name, op1):
        value = op1[0]
        argName = name[0]
        frameName = argName.split('@',1)[0]
        variableName = argName.split('@',1)[1]
        if str(value) == "None":
            value = str()
        self.checkVariable(argName)
        
        if frameName == "GF":
            self.GF.variables.update({variableName : value})
                
        elif frameName == "LF":
             self.LF.variables.update({variableName : value})
                
        elif frameName == "TF":
            self.TF.variables.update({variableName : value})
                
    def checkVariable(self, variable):
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
            elif variableName not in self.LF.variables.keys():
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
        
                
    #def 
            
            
        
                   
class Instruction:
    def __init__(self, name, args):
        self.name = name
        self.args = args
       # self.counter += 1
       # print(self.counter)
        

    
    
if __name__ == '__main__':
    main()
    