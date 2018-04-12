
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
        argList.append(argumentXML.text)
    opcode = instructionXML.attrib.get("opcode")
    
    inst = Instruction(opcode, argList)
    return inst
    
def interpret(frameStack, instList):
    for instruction in instList:
        if instruction.name == "DEFVAR":
            frameStack.addVariable(instruction.args[0])
        elif instruction.name == "MOVE":
            frameStack.initVariable(instruction.args[0], instruction.args[1])
        
        
    
    
        
class Frame:
    def __init__(self):
        self.variables = dict()
        
   # def addVariable(self, variableName):
    #    self.variables.get(variableName, "not init")
        
class variableTable:
    def __init__(self):
        self.GF = Frame()
        self.LF = list()
        self.TF = Frame()
    
    def addVariable(self, arg):
        frameName = arg.split('@',1)[0]
        if frameName == "GF":
            self.GF.variables.get(arg.split('@',1)[1], "not init")
        elif frameName == "LF":
            if not self.LF:
                exit(55)
            else:
                self.LF.variables.get(arg.split('@',1)[1], "not init")
        elif frameName == "TF":
            self.TF.variables.get(arg.split('@',1)[1], "not init")
            
    def initVariable(self, name, value):
        frameName = name.split('@',1)[0]
        variableName = name.split('@',1)[1]
        if str(value) == "None":
            value = str()
            
        self.checkVariable(name)
        
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
                
        elif frameName == "LF":
            if not self.LF:
                exit(55)
            elif variableName not in self.LF.variables.keys():
                exit(54)
                
        elif frameName == "TF":
            if variableName not in self.TF.variables.keys():
                exit(54)
            
            
        
                   
class Instruction:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        

    
    
if __name__ == '__main__':
    main()
    