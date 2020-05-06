'''
This script contains our value classes
'''
from helper import *
from env import *
from exp import *
import math

class NextIteration(Exception):
    '''
    NextIteration is a special type of exception that we raise while evaluating
    loops. It signifies a transition to a loop's next iteration
    '''
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def __str__(self):
        return "NextIteration has been raised"

class Value:
    '''
    The Value class is the parent class for all the value types and defines type
    checks, display, and returning the value
    '''
    def __init__(self):
        pass
    def __str__(self):
        pass
    def __eq__(self, other):
        pass
    def isBoolean(self):
        return False
    def isRational(self):
        return False
    def isFloat(self):
        return False
    def isString(self):
        return False
    def isNil(self):
        return False
    def isProcedure(self):
        return False
    def isRefCell(self):
        return False
    def isVector(self):
        return False
    def isDistribution(self):
        return False
    def toDisplay(self):
        pass
    def getBoolean(self):
        runtimeError("Value " + str(self) + " is not of type BOOLEAN")
    def getNumerator(self):
        runtimeError("Value " + str(self) + " is not of type RATIONAL")
    def getDenominator(self):
        runtimeError("Value " + str(self) + " is not of type RATIONAL")
    def getFloat(self):
        runtimeError("Value " + str(self) + " is not of type FLOAT")
    def getString(self):
        runtimeError("Value " + str(self) + " is not of type STRING")
    def getRefContent(self):
        runtimeError("Value " + str(self) + " is not of type REFCELL")
    def putRefContent(self, v):
        runtimeError("Value " + str(self) + " is not of type REFCELL")
    def apply(self, vs):
        runtimeError("Value " + str(self) + " is not of type PROCEDURE")

class VBoolean(Value):
    '''
    The VBoolean class defines our boolean (true/false) values
    '''
    def __init__(self, b):
        self.val = b
    def __str__(self):
        return "VBoolean[" + str(self.val) + "]"
    def __eq__(self, other):
        other.val == self.val
    def isBoolean(self):
        return True
    def getBoolean(self):
        return self.val
    def toDisplay(self):
        if self.val:
            return "true"
        return "false"

class VRational(Value):
    '''
    The VRational class defines our rational values, i.e. fractions
    '''
    def __init__(self, num, den):
        self.num = num
        self.den = den
    def __str__(self):
        return "VFraction[" + str(self.num) + ", " + str(self.den) + "]"
    def __eq__(self, other):
        self.num == other.num and self.den == other.den
    def isRational(self):
        return True
    def getNumerator(self):
        return self.num
    def getDenominator(self):
        return self.den
    def toDisplay(self):
        return str(self.num) + "/" + str(self.den)
    def gcd(n, m):
        if m == 0:
            return n
        elif n == 0:
            return m
        elif m > n:
            return gcd(m % n, n)
        else:
            return gcd(m, n % m)
    def sign(n):
        if n < 0:
            return -1
        return 1
    def abs(n):
        if n < 0:
            return -n
        return n
    def simplify():
        s = sign(self.num)*sign(self.den)
        g = gcd(abs(self.num), abs(self.den))
        sn = abs(self.num) / g
        sd = abs(self.den) / g
        if sd == 1:
            return VFloat(s*sn)
        return VRational(s*sn, sd)

class VFloat(Value):
    '''
    The VFloat class defines our float values, i.e. decimals
    '''
    def __init__(self, f):
        self.val = float(f)
    def __str__(self):
        return "VFloat[" + str(self.val) + "]"
    def __eq__(self, other):
        return math.isclose(other.val, self.val)
    def isFloat(self):
        return True
    def toDisplay(self):
        return str(self.val)
    def getFloat(self):
        return self.val

class VString(Value):
    '''
    The VString class defines our string values
    '''
    def __init__(self, s):
        self.val = s
    def __str__(self):
        return "VString[" + self.val + "]"
    def __eq__(self, other):
        other.val == self.val
    def isString(self):
        return True
    def toDisplay(self):
        return '\"' + self.val + '\"'
    def getString(self):
        return self.val

class VNil(Value):
    '''
    The VNil class defines our nil or None value
    '''
    def __init__(self):
        self.val = None
    def __str__(self):
        return "VNil[" + str(self.val) + "]"
    def __eq__(self, other):
        other.val == self.val
    def isNil(self):
        return True
    def toDisplay(self):
        return str(self.val)

class VProcedure(Value):
    '''
    The VProcedure class defines our procedures or functions
    '''
    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env
    def __str__(self):
        return "VProcedure[" + self.name + "; " + ','.join([str(elm) for elm in self.params]) + "; " + str(self.body) + "; " + str(self.env) + "]"
    def __eq__(self, other):
        runtimeError("Equal for VProcedure not implemented yet")
    def isProcedure(self):
        return True
    def toDisplay(self):
        return "#PROCEDURE"
    def apply(self, args):
        if len(self.params) != len(args):
            runtimeError("wrong number of arguments\n  Function " + str(self))
        new_env = self.env
        for (p,v) in zip(self.params, args):
            new_env = new_env.push(p,v)
        new_env = new_env.push(self.name, self)
        return self.body.eval(new_env)

class VDistribution(Value):
    '''
    The VDistribution class defines our primitive distributions before sampling
    '''
    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env
    def __str__(self):
        return "VDistribution[" + self.name + "; " + ','.join([str(elm) for elm in self.params]) + "; " + str(self.body) + "; " + str(self.env) + "]"
    def __eq__(self, other):
        runtimeError("Equal for VDistribution not implemented yet")
    def isDistribution(self):
        return True
    def toDisplay(self):
        return str(self)
    def apply(self, args):
        if len(self.params) != len(args):
            runtimeError("wrong number of arguments\n  Function " + str(self))
        new_env = self.env
        for (p,v) in zip(self.params, args):
            new_env = new_env.push(p,v)
        new_env = new_env.push(self.name, self)
        return self.body.eval(new_env)

class VRefCell(Value):
    '''
    The VRefCell class defines our reference cells
    '''
    def __init__(self, init):
        self.content = init
    def __str__(self):
        return "VRefCell[" + str(self.content) + "]"
    def __eq__(self, other):
        str(other.val) == str(self)
    def isRefCell(self):
        return True
    def toDisplay(self):
        return "#REF[" + str(self.content) + "]"
    def getRefContent(self):
        return self.content
    def putRefContent(self, v):
        self.content = v

class VPrimitive(Value):
    '''
    The VPrimitive class defines our primitive operations or python functions
    '''
    def __init__(self, oper):
        self.oper = oper
    def __str__(self):
        return "VPrimitive[" + str(self.oper) + "]"
    def __eq__(self, other):
        runtimeError("Equal for VPrimitive not implemented yet")
    def isProcedure(self):
        return True
    def toDisplay(self):
        return "#PRIMITIVE[" + str(self.oper) + "]"
    def apply(self, args):
        return self.oper(args)

class VVector(Value):
    '''
    The VVector class defines our vectors
    '''
    def __init__(self, l):
        self.list = l
    def __str__(self):
        return "VVector[" + ', '.join([str(elm) for elm in self.list]) + "]"
    def __eq__(self, other):
        if other.isVector():
            if len(other.getList()) == len(self.list):
                for index, elm in enumerate(self.list):
                    if elm != other.getList()[index]:
                        return False
                return True
        return False
    def isVector(self):
        return True
    def getList(self):
        return self.list
    def toDisplay(self):
        return "(" + ', '.join([elm.toDisplay() for elm in self.list]) + ")"

class VLoop(Value):
    '''
    The VLoop class defines our loops
    '''
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "VLoop[" + str(self.name) + "]"
    def __eq__(self, other):
        runtimeError("Equal for VLoop not implemented yet")
    def toDisplay(self):
        return "#LOOP[" + str(self.name) + "]"
    def apply(self, args):
        raise NextIteration(self.name, args)
