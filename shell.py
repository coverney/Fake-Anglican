'''
This script contains our interactive shell and primitive operations
'''
from helper import *
from exp import *
from value import *
from env import *
from parsita import *
from parsita.util import constant
import string
import random
from our_parser import *
import math
import numpy as np
import re

def checkNumberArgs(vs, num):
    '''
    Throws an error if the length of vs is not the same as num
    '''
    if len(vs) != num:
        runtimeError("Wrong number of arguments " + str(len(vs)) + " - expected " + str(num))

def checkFloat(v):
    '''
    Throws an error if v is not a VFloat
    '''
    if not v.isFloat():
        runtimeError("Value " + str(v) + " is not of type FLOAT")

def checkRational(v):
    '''
    Throws an error if v is not a VRational
    '''
    if not v.isRational():
        runtimeError("Value " + str(v) + " is not of type RATIONAL")

def checkBoolean(v):
    '''
    Throws an error if v is not a VBoolean
    '''
    if not v.isBoolean():
        runtimeError("Value " + str(v) + " is not of type BOOLEAN")

def checkString(v):
    '''
    Throws an error if v is not a VString
    '''
    if not v.isString():
        runtimeError("Value " + str(v) + " is not of type STRING")

def checkProcedure(v):
    '''
    Throws an error if v is not a VProcedure
    '''
    if not v.isProcedure():
        runtimeError("Value " + str(v) + " is not of type PROCEDURE")

def checkRefCell(v):
    '''
    Throws an error if v is not a VRefCell
    '''
    if not v.isRefCell():
        runtimeError("Value " + str(v) + " is not of type REFCELL")

def checkVector(v):
    '''
    Throws an error if v is not a VVector
    '''
    if not v.isVector():
        runtimeError("Value " + str(v) + " is not of type VECTOR")

def checkDistribution(v):
    '''
    Throws an error if v is not a VDistribution
    '''
    if not v.isDistribution():
        runtimeError("Value " + str(v) + " is not of type DISTRIBUTION")

def convertFloat(v):
    '''
    If v is a VRational or VFloat, we convert its value to a python float
    and return it
    '''
    if v.isFloat():
        rational_float_v = v.getFloat()
    elif v.isRational():
        rational_float_v = float(v.getNumerator()/v.getDenominator())
    else:
        runtimeError("Value " + str(v) + " is not of type RATIONAL or FLOAT")
    return rational_float_v

def operMinus(vs):
    '''
    operMinus is a primitive operation that takes one argument and
    evaluates to the negative form of that argument
    e.g. (- 5) evaluates to -5, (- (- 5)) evaluates to 5
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isRational():
        return VRational(-v1.getNumerator(), v1.getDenominator()).simplify()
    elif v1.isFloat():
        return VFloat(-1*v1.getFloat())
    elif v1.isDistribution():
        body = EMultiple([v1.body], operMinus)
        return VDistribution("", v1.params, body, v1.env)
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operPlus(vs):
    '''
    operPlus is a primitive operation that takes two arguments and
    evaluates to the sum of those two arguments
    e.g. (+ 1, 2) evaluates to 3
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1.isRational() and v2.isRational():
        n1 = v1.getNumerator()
        n2 = v2.getNumerator()
        d1 = v1.getDenominator()
        d2 = v2.getDenominator()
        return VRational(n1 * d2 + n2 * d1, d1 * d2).simplify()
    elif v1.isFloat() and v2.isFloat():
        return VFloat(v1.getFloat()+v2.getFloat())
    elif v1.isFloat() and v2.isRational():
        n2 = v2.getNumerator()
        d2 = v2.getDenominator()
        return VFloat(v1.getFloat()+float(n2/d2))
    elif v2.isFloat() and v1.isRational():
        n1 = v1.getNumerator()
        d1 = v1.getDenominator()
        return VFloat(v2.getFloat()+float(n1/d1))
    elif v1.isDistribution() and v2.isDistribution():
        # new distribution should have combined params and env of v1 & v2
        new_env = Env(v1.env.content+v2.env.content)
        body = EMultiple([v1.body, v2.body], operPlus)
        return VDistribution("", v1.params+v2.params, body, new_env)
    elif v1.isDistribution() and (v2.isRational() or v2.isFloat()):
        v2_float = convertFloat(v2)
        body = EMultiple([v1.body, EFloat(v2_float)], operPlus)
        return VDistribution("", v1.params, body, v1.env)
    elif v2.isDistribution() and (v1.isRational() or v1.isFloat()):
        v1_float = convertFloat(v1)
        body = EMultiple([v2.body, EFloat(v1_float)], operPlus)
        return VDistribution("", v2.params, body, v2.env)
    else:
        runtimeError("Value " + str(v1) + " and/or " + str(v2) + " is not of type RATIONAL or FLOAT or PRIMITIVE or DISTRIBUTION")

def operTimes(vs):
    '''
    operTimes is a primitive operation that takes two arguments and
    evaluates to the product of those two arguments
    e.g. (* 2, 3) evaluates to 6
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1.isRational() and v2.isRational():
        n1 = v1.getNumerator()
        n2 = v2.getNumerator()
        d1 = v1.getDenominator()
        d2 = v2.getDenominator()
        return VRational(n1 * d2 + n2 * d1, d1 * d2).simplify()
    elif v1.isFloat() and v2.isFloat():
        return VFloat(v1.getFloat()*v2.getFloat())
    elif v1.isFloat() and v2.isRational():
        n2 = v2.getNumerator()
        d2 = v2.getDenominator()
        return VFloat(v1.getFloat()*float(n2/d2))
    elif v2.isFloat() and v1.isRational():
        n1 = v1.getNumerator()
        d1 = v1.getDenominator()
        return VFloat(v2.getFloat()*float(n1/d1))
    elif v1.isDistribution() and v2.isDistribution():
        # new distribution should have combined params and env of v1 & v2
        new_env = Env(v1.env.content+v2.env.content)
        body = EMultiple([v1.body, v2.body], operTimes)
        return VDistribution("", v1.params+v2.params, body, new_env)
    elif v1.isDistribution() and (v2.isRational() or v2.isFloat()):
        v2_float = convertFloat(v2)
        body = EMultiple([v1.body, EFloat(v2_float)], operTimes)
        return VDistribution("", v1.params, body, v1.env)
    elif v2.isDistribution() and (v1.isRational() or v1.isFloat()):
        v1_float = convertFloat(v1)
        body = EMultiple([v2.body, EFloat(v1_float)], operTimes)
        return VDistribution("", v2.params, body, v2.env)
    else:
        runtimeError("Value " + str(v1) + " and/or " + str(v2) + " is not of type RATIONAL or FLOAT")

def operDiv(vs):
    '''
    operDiv is a primitive operation that takes two arguments and
    evaluates to the quotient resulting from dividing the first argument
    by the second argument
    e.g. (/ 6, 3) evaluates to 2
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1.isRational() and v2.isRational():
        n1 = v1.getNumerator()
        n2 = v2.getNumerator()
        d1 = v1.getDenominator()
        d2 = v2.getDenominator()
        return VRational(n1 * d2, n2 * d1).simplify()
    elif v1.isFloat() and v2.isFloat():
        return VFloat(v1.getFloat()/v2.getFloat())
    elif v1.isFloat() and v2.isRational():
        n2 = v2.getNumerator()
        d2 = v2.getDenominator()
        return VFloat(v1.getFloat()/float(n2/d2))
    elif v2.isFloat() and v1.isRational():
        n1 = v1.getNumerator()
        d1 = v1.getDenominator()
        return VFloat(float(n1/d1)/v2.getFloat())
    elif v1.isDistribution() and v2.isDistribution():
        # new distribution should have combined params and env of v1 & v2
        new_env = Env(v1.env.content+v2.env.content)
        body = EMultiple([v1.body, v2.body], operDiv)
        return VDistribution("", v1.params+v2.params, body, new_env)
    elif v1.isDistribution() and (v2.isRational() or v2.isFloat()):
        v2_float = convertFloat(v2)
        body = EMultiple([v1.body, EFloat(v2_float)], operDiv)
        return VDistribution("", v1.params, body, v1.env)
    elif v2.isDistribution() and (v1.isRational() or v1.isFloat()):
        v1_float = convertFloat(v1)
        body = EMultiple([v2.body, EFloat(v1_float)], operDiv)
        return VDistribution("", v2.params, body, v2.env)
    else:
        runtimeError("Value " + str(v1) + " and/or " + str(v2) + " is not of type RATIONAL or FLOAT")

def operEqual(vs):
    '''
    operEqual is a primitive operation that takes two arguments and
    returns true if the two arguments are equal and false otherwise
    e.g. (= 2, 2) evaluates to true, (= 2, 3) evaluates to false
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1 == v2:
        return VBoolean(True)
    return VBoolean(False)

def operNotEqual(vs):
    '''
    operNotEqual is a primitive operation that takes two arguments and
    returns true if the two arguments are not equal and false otherwise
    e.g. (~= 2, 2) evaluates to false, (~= 2, 3) evaluates to true
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1 == v2:
        return VBoolean(False)
    return VBoolean(True)

def operLess(vs):
    '''
    operLess is a primitive operation that takes two arguments and
    returns true if the first argument is less than the second and false otherwise
    e.g. (< 3, 2) evaluates to false, (< 2, 3) evaluates to true
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1.isRational() and v2.isRational():
        n1 = v1.getNumerator()
        n2 = v2.getNumerator()
        d1 = v1.getDenominator()
        d2 = v2.getDenominator()
        return VBoolean(n1 * d2 < n2 * d1)
    elif v1.isFloat() and v2.isFloat():
        return VBoolean(v1.getFloat() < v2.getFloat())
    elif v1.isFloat() and v2.isRational():
        n2 = v2.getNumerator()
        d2 = v2.getDenominator()
        return VBoolean(v1.getFloat() < float(n2/d2))
    elif v2.isFloat() and v1.isRational():
        n1 = v1.getNumerator()
        d1 = v1.getDenominator()
        return VFloat(float(n1/d1) < v2.getFloat())
    else:
        runtimeError("Value " + str(v1) + " and/or " + str(v2) + " is not of type RATIONAL or FLOAT")

def operGreater(vs):
    '''
    operGreater is a primitive operation that takes two arguments and
    returns true if the first argument is greater than the second and false otherwise
    e.g. (> 3, 2) evaluates to true, (> 2, 3) evaluates to false
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1.isRational() and v2.isRational():
        n1 = v1.getNumerator()
        n2 = v2.getNumerator()
        d1 = v1.getDenominator()
        d2 = v2.getDenominator()
        return VBoolean(n1 * d2 > n2 * d1)
    elif v1.isFloat() and v2.isFloat():
        return VBoolean(v1.getFloat() > v2.getFloat())
    elif v1.isFloat() and v2.isRational():
        n2 = v2.getNumerator()
        d2 = v2.getDenominator()
        return VBoolean(v1.getFloat() > float(n2/d2))
    elif v2.isFloat() and v1.isRational():
        n1 = v1.getNumerator()
        d1 = v1.getDenominator()
        return VFloat(float(n1/d1) > v2.getFloat())
    else:
        runtimeError("Value " + str(v1) + " and/or " + str(v2) + " is not of type RATIONAL or FLOAT")

def operLessEq(vs):
    '''
    operLessEq is a primitive operation that takes two arguments and
    returns true if the first argument is less than or equal to the second
    and false otherwise
    e.g. (<= 3, 2) evaluates to false, (<= 2, 3) and (<= 2, 2) evaluate to true
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1.isRational() and v2.isRational():
        n1 = v1.getNumerator()
        n2 = v2.getNumerator()
        d1 = v1.getDenominator()
        d2 = v2.getDenominator()
        return VBoolean(n1 * d2 <= n2 * d1)
    elif v1.isFloat() and v2.isFloat():
        return VBoolean(v1.getFloat() <= v2.getFloat())
    elif v1.isFloat() and v2.isRational():
        n2 = v2.getNumerator()
        d2 = v2.getDenominator()
        return VBoolean(v1.getFloat() <= float(n2/d2))
    elif v2.isFloat() and v1.isRational():
        n1 = v1.getNumerator()
        d1 = v1.getDenominator()
        return VFloat(float(n1/d1) <= v2.getFloat())
    else:
        runtimeError("Value " + str(v1) + " and/or " + str(v2) + " is not of type RATIONAL or FLOAT")

def operGreaterEq(vs):
    '''
    operGreaterEq is a primitive operation that takes two arguments and
    returns true if the first argument is greater than or equal to the second
    and false otherwise
    e.g. (>= 3, 2) and (>= 2, 2) evaluate to true, (>= 2, 3) evaluates to false
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    if v1.isRational() and v2.isRational():
        n1 = v1.getNumerator()
        n2 = v2.getNumerator()
        d1 = v1.getDenominator()
        d2 = v2.getDenominator()
        return VBoolean(n1 * d2 >= n2 * d1)
    elif v1.isFloat() and v2.isFloat():
        return VBoolean(v1.getFloat() >= v2.getFloat())
    elif v1.isFloat() and v2.isRational():
        n2 = v2.getNumerator()
        d2 = v2.getDenominator()
        return VBoolean(v1.getFloat() >= float(n2/d2))
    elif v2.isFloat() and v1.isRational():
        n1 = v1.getNumerator()
        d1 = v1.getDenominator()
        return VFloat(float(n1/d1) >= v2.getFloat())
    else:
        runtimeError("Value " + str(v1) + " and/or " + str(v2) + " are not of type RATIONAL or FLOAT")

def operRefCell(vs):
    '''
    operRefCell is a primitive operation that defines a reference cell
    '''
    checkNumberArgs(vs, 1)
    init = vs[0]
    return VRefCell(init)

def operGetRefCell(vs):
    '''
    operGetRefCell is a primitive operation that returns the value from the
    indicated reference cell
    '''
    checkNumberArgs(vs, 1)
    r = vs[0]
    checkRefCell(r)
    return r.getRefContent()

def operPutRefCell(vs):
    '''
    operPutRefCell is a primitive operation that puts a value (second argument)
    in the indicated reference cell (first argument)
    '''
    checkNumberArgs(vs, 2)
    r = vs[0]
    v = vs[1]
    checkRefCell(r)
    r.putRefContent(v)
    return VBoolean(True)

def operPrint(vs):
    '''
    operPrint is a primitive operation that takes in a list of argument(s) and
    prints the argument(s)
    '''
    output = []
    for v in vs:
        output.append(v.toDisplay())
    print(' '.join(output))
    return VBoolean(True)

def operConcat(vs):
    '''
    operConcat is a primitive operation that takes in a list of string argument(s) and
    concatenates the argument(s)
    '''
    newstring = ""
    for v in vs:
        checkString(v)
        newstring += v.getString()
    return VString(newstring)

def operLower(vs):
    '''
    operLower is a primitive operation that takes in a string argument and
    turns all the characters into lowercase
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkString(v1)
    return VString(v1.getString().lower())

def operUpper(vs):
    '''
    operUpper is a primitive operation that takes in a string argument and
    turns all the characters into uppercase
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkString(v1)
    return VString(v1.getString().upper())

def operSubstring(vs):
    '''
    operSubstring is a primitive operation that takes in a string argument and
    two numerical arguments and returns the substring from the first numerical
    argument to the second
    '''
    checkNumberArgs(vs, 3)
    v1 = vs[0]
    checkString(v1)
    v2 = vs[1]
    v3 = vs[2]
    rational_float_v2 = convertFloat(v2)
    rational_float_v3 = convertFloat(v3)
    if not rational_float_v2.is_integer() or not rational_float_v3.is_integer():
        runtimeError(f"Values {str(v2)} and/or {str(v3)} are not integers")
    try:
        return VString(v1.getString()[int(rational_float_v2): int(rational_float_v3)]) # kinda weird!
    except:
        runtimeError(f"Values {str(v2)} and {str(v3)} are invalid indices")

def operEven(vs):
    '''
    operEven is a primitive operation that takes in a numerical argument and
    checks whether it is even
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VBoolean(v1.getFloat() % 2 == float(0))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VBoolean(rational_float % 2 == float(0))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operOdd(vs):
    '''
    operOdd is a primitive operation that takes in a numerical argument and
    checks whether it is odd
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VBoolean(v1.getFloat() % 2 == float(1))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VBoolean(rational_float % 2 == float(1))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")


def operLog(vs):
    '''
    operLog is a primitive operation that takes in a numerical argument and
    evaluates to the natural log of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.log(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.log(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operLog10(vs):
    '''
    operLog10 is a primitive operation that takes in a numerical argument and
    evaluates to the log base 10 of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.log(v1.getFloat(), 10))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.log(rational_float, 10))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operExp(vs):
    '''
    operExp is a primitive operation that takes in a numerical argument and
    evaluates to the exponential (e^x) of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.exp(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.exp(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operPow(vs):
    '''
    operPow is a primitive operation that takes in two numerical arguments and
    returns the result of the first argument evaluated to the power of the second
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    rational_float_v1 = convertFloat(v1)
    rational_float_v2 = convertFloat(v2)
    return VFloat(pow(rational_float_v1, rational_float_v2))

def operSqrt(vs):
    '''
    operSqrt is a primitive operation that takes in a numerical argument and
    evaluates to the square root of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.sqrt(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.sqrt(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operCbrt(vs):
    '''
    operCbrt is a primitive operation that takes in a numerical argument and
    evaluates to the cubic root of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat((v1.getFloat())**(1/3))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat((rational_float)**(1/3))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operFloor(vs):
    '''
    operFloor is a primitive operation that takes in a numerical argument and
    evaluates to the floor of that argument (the greatest integer less than or equal to)
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.floor(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.floor(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operCeil(vs):
    '''
    operCeil is a primitive operation that takes in a numerical argument and
    evaluates to the ceiling of that argument (the least integer greater than or equal to)
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.ceil(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.ceil(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operRound(vs):
    '''
    operRound is a primitive operation that takes in two numerical arguments and
    rounds the first argument to the decimal place indicated by the second (integer)
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0] # should be float
    v2 = vs[1] # should be integer
    rational_float_v1 = convertFloat(v1)
    rational_float_v2 = convertFloat(v2)
    if rational_float_v2.is_integer():
        return VFloat(round(rational_float_v1, int(rational_float_v2)))
    else:
        runtimeError("Value " + str(v2) + " is not a integer")

def operRint(vs):
    '''
    operRint is a primitive operation that takes in a numerical argument and
    rounds it to the nearest integer
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    rational_float_v1 = convertFloat(v1)
    return VFloat(int(round(rational_float_v1)))


def operAbs(vs):
    '''
    operAbs is a primitive operation that takes in a numerical argument and
    evaluates to the absolute value of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(abs(v1.getFloat()))
    elif v1.isRational():
        num = abs(v1.getNumerator())
        den = abs(v1.getDenominator())
        return VRational(num, den)
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operSignum(vs):
    '''
    operSignum is a primitive operation that takes in a numerical argument and
    returns the sign of the value as either 1.0 or -1.0
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.copysign(1, v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.copysign(1, rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operSin(vs):
    '''
    operSin is a primitive operation that takes in a numerical argument and
    evaluates the sine in radians of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.sin(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.sin(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operCos(vs):
    '''
    operCos is a primitive operation that takes in a numerical argument and
    evaluates the cosine in radians of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.cos(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.cos(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operTan(vs):
    '''
    operTan is a primitive operation that takes in a numerical argument and
    evaluates the tangent in radians of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.tan(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.tan(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operAsin(vs):
    '''
    operAsin is a primitive operation that takes in a numerical argument and
    evaluates the arc sine of that argument in radians
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.asin(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.asin(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operAcos(vs):
    '''
    operAcos is a primitive operation that takes in a numerical argument and
    evaluates the arc cosine of that argument in radians
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.acos(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.acos(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operAtan(vs):
    '''
    operAtan is a primitive operation that takes in a numerical argument and
    evaluates the arc tangent of that argument in radians
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.atan(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.atan(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operSinh(vs):
    '''
    operSinh is a primitive operation that takes in a numerical argument and
    evaluates the hyperbolic sine in radians of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.sinh(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.sinh(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operCosh(vs):
    '''
    operCosh is a primitive operation that takes in a numerical argument and
    evaluates the hyperbolic cosine in radians of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.cosh(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.cosh(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operTanh(vs):
    '''
    operCosh is a primitive operation that takes in a numerical argument and
    evaluates the hyperbolic tangent in radians of that argument
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(math.tanh(v1.getFloat()))
    elif v1.isRational():
        rational_float = float(v1.getNumerator()/v1.getDenominator())
        return VFloat(math.tanh(rational_float))
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operInc(vs):
    '''
    operInc is a primitive operation that takes in a numerical argument and
    increments it by 1
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(v1.getFloat()+1)
    elif v1.isRational():
        return VRational(v1.getNumerator()+v1.getDenominator(), v1.getDenominator()).simplify()
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operDec(vs):
    '''
    operDec is a primitive operation that takes in a numerical argument and
    decrements it by 1
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    if v1.isFloat():
        return VFloat(v1.getFloat()-1)
    elif v1.isRational():
        return VRational(v1.getNumerator()-v1.getDenominator(), v1.getDenominator()).simplify()
    else:
        runtimeError("Value " + str(v1) + " is not of type RATIONAL or FLOAT")

def operMod(vs):
    '''
    operMod is a primitive operation that takes in two numerical arguments and
    returns the value of the first argument modulo the second
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    rational_float_v1 = convertFloat(v1)
    rational_float_v2 = convertFloat(v2)
    return VFloat(rational_float_v1 % rational_float_v2)

def operSum(vs):
    '''
    operSum is a primitive operation that takes in a list of numerical arguments and
    returns the sum of those arguments
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    l = v1.getList()
    sum = 0
    for elm in l:
        if elm.isFloat():
            sum += elm.getFloat()
        elif elm.isRational():
            sum += float(elm.getNumerator()/ elm.getDenominator())
        else:
            runtimeError("Value " + str(elm) + " is not of type RATIONAL or FLOAT")
    return VFloat(sum)

def operCumsum(vs):
    '''
    operCumsum is a primitive operation that takes in a list of numerical arguments and
    returns a vector containing the cumulative or partial sums in sequence
    '''
    # sequence of partial sums in a sequence
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    l = v1.getList()
    newl = []
    for elm in l:
        if elm.isFloat():
            newl.append(elm.getFloat())
        elif elm.isRational():
            newl.append(float(elm.getNumerator()/ elm.getDenominator()))
        else:
            runtimeError("Value " + str(elm) + " is not of type RATIONAL or FLOAT")
    cumsum = np.cumsum(newl)
    output = []
    for elm in cumsum:
        output.append(VFloat(elm))
    return VVector(output)

def operMean(vs):
    '''
    operMean is a primitive operation that takes in a list of numerical arguments and
    returns the mean of those arguments
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    l = v1.getList()
    floats = []
    for elm in l:
        if elm.isFloat():
            floats.append(elm.getFloat())
        elif elm.isRational():
            floats.append(float(elm.getNumerator()/elm.getDenominator()))
        else:
            runtimeError("Value " + str(elm) + " is not of type RATIONAL or FLOAT")
    return VFloat(sum(floats)/len(floats))

def operNormalize(vs):
    '''
    operNormalize is a primitive operation that takes a vector argument and
    returns a normalized version of the vector where its magnitude equals 1
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    l = v1.getList()
    floats = []
    for elm in l:
        if elm.isFloat():
            floats.append(elm.getFloat())
        elif elm.isRational():
            floats.append(float(elm.getNumerator()/elm.getDenominator()))
        else:
            runtimeError("Value " + str(elm) + " is not of type RATIONAL or FLOAT")
    norm = [float(i)/sum(floats) for i in floats]
    output = []
    for elm in norm:
        output.append(VFloat(elm))
    return VVector(output)

# Vector operations
def operCons(vs):
    '''
    operCons is a primitive operation that takes 2 arguments: a value and a
    vector and returns a new vector with the value appended to the front
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    checkVector(v2)
    return VVector([v1] + v2.getList())

def operFirst(vs):
    '''
    operFirst is a primitive operation that takes 1 vector argument
    and returns its first element
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    l = v1.getList()
    if len(l) < 1:
        runtimeError("cannot apply first to an empty VECTOR")
    else:
        return l[0]

def operSecond(vs):
    '''
    operSecond is a primitive operation that takes 1 vector argument
    and returns its second element
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    l = v1.getList()
    if len(l) < 2:
        runtimeError("cannot apply second to VECTOR with less than 2 elms")
    else:
        return l[1]

def operNth(vs):
    '''
    operNth is a primitive operation that takes 2 arguments: a vector and an
    index, n, and returns the nth element of the vector
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    checkVector(v1)
    rational_float_v2 = convertFloat(v2)
    if not rational_float_v2.is_integer():
        runtimeError("Value " + str(v2) + " is not a integer")
    n = int(rational_float_v2)
    l = v1.getList()
    if len(l) < n:
        runtimeError(f"cannot apply second to VECTOR with less than {n} elms")
    else:
        return l[n-1]

def operRest(vs):
    '''
    operRest is a primitive operation that takes 1 vector argument
    and returns a VVector with all but the first element
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    l = v1.getList()
    if len(l) < 1:
        runtimeError("cannot apply rest to an empty VECTOR")
    else:
        return VVector(l[1:])

def operCount(vs):
    '''
    operCount is a primitive operation that takes 1 vector argument
    and returns a VFloat representing the length of the vector
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    l = v1.getList()
    return VFloat(len(l))

def operEmptyP(vs):
    '''
    operEmptyP is a primitive operation that takes 1 vector argument
    and returns a VBoolean based on whether the list is empty or not
    (empty => true)
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    return VBoolean(len(v1.getList()) < 1)

def operSample(vs):
    '''
    operSample samples a VDistribution by calling its apply method and
    returning its result. It can take in any number of arguments depending
    on how many arguments the VDistribution requires, but the first arg
    needs to be a VDistribution
    '''
    if len(vs) > 0:
        v1 = vs[0]
        checkDistribution(v1)
        result = v1.apply(vs[1:])
        if result.isProcedure(): # it is a VPrimitive and probably a lambda function
            return result.apply([])
        else:
            return result
    else:
        runtimeError("0 arguments applied to sample")

def operNormal(vs):
    '''
    operNormal is a primitive operation that takes two float arguments
    and returns a VDistribution. The body is a EPrimitive, which is a
    wrapper for a python lambda function that calls Numpy's random.normal function
    '''
    # https://docs.scipy.org/doc/numpy-1.15.0/reference/generated/numpy.random.normal.html
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    rational_float_v1 = convertFloat(v1)
    rational_float_v2 = convertFloat(v2)
    python_func = lambda x : VFloat(np.random.normal(rational_float_v1, rational_float_v2))
    return VDistribution("", [], EPrimitive(python_func), Env())

def operPoisson(vs):
    '''
    operPoisson is a primitive operation that takes 1 float argument
    and returns a VDistribution. The body is a EPrimitive, which is a wrapper
    for a python lambda function that calls Numpy's random.poisson function
    '''
    # https://docs.scipy.org/doc/numpy-1.14.1/reference/generated/numpy.random.poisson.html
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    rational_float_v1 = convertFloat(v1)
    python_func = lambda x : VFloat(np.random.poisson(rational_float_v1))
    return VDistribution("", [], EPrimitive(python_func), Env())

def operExponential(vs):
    '''
    operExponential is a primitive operation that takes 1 float argument
    and returns a VDistribution. The body is a EPrimitive, which is a wrapper
    for a python lambda function that calls Numpy's random.exponential function
    '''
    # https://docs.scipy.org/doc/numpy-1.15.0/reference/generated/numpy.random.exponential.html
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    rational_float_v1 = convertFloat(v1)
    python_func = lambda x: VFloat(np.random.exponential(rational_float_v1))
    return VDistribution("", [], EPrimitive(python_func), Env())

def operBeta(vs):
    '''
    operBeta is a primitive operation that takes two float arguments
    and returns a VDistribution. The body is a EPrimitive, which is a
    wrapper for a python lambda function that calls Numpy's random.beta function
    '''
    # https://docs.scipy.org/doc/numpy-1.15.1/reference/generated/numpy.random.beta.html
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    rational_float_v1 = convertFloat(v1)
    rational_float_v2 = convertFloat(v2)
    python_func = lambda x : VFloat(np.random.beta(rational_float_v1, rational_float_v2))
    return VDistribution("", [], EPrimitive(python_func), Env())

def operUniformContinuous(vs):
    '''
    operUniformContinuous is a primitive operation that takes two arguments
    representing the start and end of a range and returns a VDistribution.
    The body is a EPrimitive, which is a wrapper for a python lambda function
    that calls Numpy's random.uniform function, which returns a float within
    [start, end)
    '''
    # https://docs.scipy.org/doc/numpy-1.15.0/reference/generated/numpy.random.uniform.html
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    v2 = vs[1]
    rational_float_v1 = convertFloat(v1)
    rational_float_v2 = convertFloat(v2)
    python_func = lambda x: VFloat(np.random.uniform(rational_float_v1, rational_float_v2))
    return VDistribution("", [], EPrimitive(python_func), Env())

def operUniformDiscrete(vs):
    '''
    operUniformDiscrete is a primitive operation that takes one argument representing
    a vector and returns a VDistribution. The body is a EPrimitive,
    which is a wrapper for a python lambda function that picks a random element
    from the inputted vector
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    checkVector(v1)
    elms = v1.getList()
    python_func = lambda x: elms[np.random.randint(0, len(elms))]
    return VDistribution("", [], EPrimitive(python_func), Env())

def operBernoulli(vs):
    '''
    operBernoulli is a primitive operation that takes one argument representing
    the probability of getting heads in a coin flip and returns a VDistribution.
    The body is a EPrimitive, which is a wrapper for a python lambda function
    that calls Numpy's random.binomial function
    '''
    checkNumberArgs(vs, 1)
    v1 = vs[0]
    rational_float_v1 = convertFloat(v1)
    python_func = lambda x: VFloat(np.random.binomial(1, rational_float_v1))
    return VDistribution("", [], EPrimitive(python_func), Env())

def operVector(vs):
    '''
    operVector is a primitive operation that takes a list of arguments
    and returns a VVector containing that list
    '''
    return VVector(vs)

def operMap(vs):
    '''
    operFilter is a primitive operation that takes two arguments, a procedure
    and a vector and returns a new vector that is the result of applying each
    element in the original vector to the procedure
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    checkProcedure(v1)
    v2 = vs[1]
    checkVector(v2)
    vec2 = []
    for elm in v2.getList():
        vec2.append(v1.apply([elm]))
    return VVector(vec2)

def operFilter(vs):
    '''
    operFilter is a primitive operation that takes two arguments, a procedure
    and a vector and returns a new vector that contains all of the elements of
    the previous vector which return true when applied to the procedure
    '''
    checkNumberArgs(vs, 2)
    v1 = vs[0]
    checkProcedure(v1)
    v2 = vs[1]
    checkVector(v2)
    vec2 = []
    for elm in v2.getList():
        if v1.apply([elm]).getBoolean():
            vec2.append(elm)
    return VVector(vec2)

# Define the initial environment as a list of primitive operations
initEnv = Env([
    ("-", VPrimitive(operMinus)), # (- 5)
    ("*", VPrimitive(operTimes)), # (* 2, 7)
    ("+", VPrimitive(operPlus)), # (+ 2, 4), (+ (poisson 5), (poisson 10))
    ("/", VPrimitive(operDiv)), # (/ 6, 2)
    ("=", VPrimitive(operEqual)), # (= 1, 1) (= 1, 2)
    ("~=", VPrimitive(operNotEqual)), # (~= 1, 1) (~= 1, 2)
    ("<", VPrimitive(operLess)),  # (< 1, 1) (< 1, 2) (< 2, 1)
    (">", VPrimitive(operGreater)), # (> 1, 1) (> 1, 2) (> 2, 1)
    ("<=", VPrimitive(operLessEq)), # (<= 1, 1) (<= 1, 2) (<= 2, 1)
    (">=", VPrimitive(operGreaterEq)), # (>= 1, 1) (>= 1, 2) (>= 2, 1)
    ("ref", VPrimitive(operRefCell)), # (ref 1_3)
    ("get", VPrimitive(operGetRefCell)), # (get (ref 5.5))
    ("put", VPrimitive(operPutRefCell)), # (put (ref 5.5), 2)
    ("print", VPrimitive(operPrint)), # (print "hi")
    ("concat", VPrimitive(operConcat)), # (concat "hell", "o")
    ("lower", VPrimitive(operLower)), # (lower "HELLO") (lower "hEllO")
    ("upper", VPrimitive(operUpper)), # (upper "hello") (upper "hEllO")
    ("substring", VPrimitive(operSubstring)), # (substring "hello world", 0, 3)
    ("even", VPrimitive(operEven)), # (even 2) (even 5)
    ("odd", VPrimitive(operOdd)), # (odd 2) (odd 5)
    ("log", VPrimitive(operLog)), # (log (exp 4))
    ("log10", VPrimitive(operLog10)), # (log10 10)
    ("exp", VPrimitive(operExp)), # (exp (log 4))
    ("^", VPrimitive(operPow)), # (^ 3, 4)
    ("sqrt", VPrimitive(operSqrt)), # (sqrt 4)
    ("cbrt", VPrimitive(operCbrt)), # (cbrt 8)
    ("floor", VPrimitive(operFloor)), # (floor 3.01) (floor 2.99)
    ("ceil", VPrimitive(operCeil)), # (ceil 3.01) (ceil 2.99)
    ("round", VPrimitive(operRound)), # (round 4.58372, 2) (round 4.58372, 4)
    ("rint", VPrimitive(operRint)), # (rint 4.58372) (rint 4.18372)
    ("abs", VPrimitive(operAbs)), # (abs (- 8)) (abs 8)
    ("sign", VPrimitive(operSignum)), # (sign (- 8)) (sign 8)
    ("sin", VPrimitive(operSin)), # (sin 0) (sin 1)
    ("cos", VPrimitive(operCos)), # (cos 0) (cos 1)
    ("tan", VPrimitive(operTan)), # (tan 0) (tan 1)
    ("asin", VPrimitive(operAsin)), # (asin 0) (asin 1)
    ("acos", VPrimitive(operAcos)), # (acos 0) (acos 1)
    ("atan", VPrimitive(operAtan)), # (atan 0) (atan 1)
    ("sinh", VPrimitive(operSinh)), # (sinh 0.25)
    ("cosh", VPrimitive(operCosh)), # (cosh 0.25)
    ("tanh", VPrimitive(operTanh)), # (tanh 0)
    ("++", VPrimitive(operInc)), # (++ 1)
    ("--", VPrimitive(operDec)), # (-- 10)
    ("%", VPrimitive(operMod)), # (begin (print (% 4, 2)), (print (% 5, 2)), (print (% 17, 5)))
    ("sum", VPrimitive(operSum)), # (sum (vector 1, 2, 3, 4))
    ("cumsum", VPrimitive(operCumsum)), # (cumsum (vector 1, 2, 3, 4))
    ("mean", VPrimitive(operMean)), # (mean (vector 1, 2, 3, 4))
    ("norm", VPrimitive(operNormalize)), # (norm (vector 1, 2, 3, 4))
    ("cons", VPrimitive(operCons)), # (cons "hello", (cons "world", (cons "!", empty)))
    ("first", VPrimitive(operFirst)), # (first (vector 1, 2, 3, 4))
    ("second", VPrimitive(operSecond)), # (second (vector 1, 2, 3, 4))
    ("nth", VPrimitive(operNth)), # (nth (vector 1, 2, 3, 4), 3)
    ("rest", VPrimitive(operRest)), # (rest (vector 1, 2, 3, 4))
    ("count", VPrimitive(operCount)), # (count (vector 1, 2, 3, 4))
    ("empty?", VPrimitive(operEmptyP)), # (empty? (vector)) (empty? (vector 1))
    ("beta", VPrimitive(operBeta)), # (sample (beta 2, 3))
    ("bernoulli", VPrimitive(operBernoulli)), # (sample (bernoulli 1_2))
    ("exponential", VPrimitive(operExponential)), # (sample (exponential 1_250))
    ("normal", VPrimitive(operNormal)), # (sample (normal 0, 0.1))
    ("poisson", VPrimitive(operPoisson)), # (sample (poisson 5))
    ("uniform", VPrimitive(operUniformContinuous)), # (sample (uniform 0, 100))
    ("randelm", VPrimitive(operUniformDiscrete)), # (sample (randelm (vector 5, 6, 7, 8))), (sample (randelm (vector "this", "is", "a", "vector")))
    ("not", VProcedure("", ["a"], EIf(EId("a"), EBoolean(False), EBoolean(True)), Env())), # (not false)
    ("vector", VPrimitive(operVector)), # (vector (+ 1, 2), (+ 3, 4), (+ 4, 5))
    ("map", VPrimitive(operMap)), # (map (lambda (a) (* a, a)), (vector 1, 2, 3, 4))
    ("filter", VPrimitive(operFilter)), # (filter (lambda (a) (not (< a, 0))), (vector 1, -2, 3, -4, 5, -6, 7))
    ("empty", VVector([])),
    ("sample", VPrimitive(operSample)),
])

def shell():
    '''
    The shell keeps asking for user input, parses the input into an expression,
    evaluates the expression to a value using the initEnv, and displays the value
    in a human readable format
    '''
    env = initEnv
    print("Type #quit to quit")
    print("Type #parse in front of expression to print its abstract representation")
    print("Type #file in front of filename to read and evaluate content of file")
    while True:
        user_input = input("PROB> ")
        try:
            if user_input.startswith("#quit"):
                return
            elif user_input.startswith("#file"): # '../test-loop-sum-squares.func'
                filename = user_input[6:]
                f = open(filename, "r")
                content_list = f.read().splitlines()
                content = ''
                for i in content_list:
                    content += i
                f.close()
                content = re.sub(' +', ' ', content)
                e = parse(content)
                print(e)
                v = e.eval(env)
                print(v.toDisplay())
            elif user_input.startswith("#parse"):
                valid_input = user_input[7:]
                e = parse(valid_input)
                print(e)
            else:
                e = parse(user_input)
                v = e.eval(env)
                print(v.toDisplay())
        except Exception as e:
            print(str(e))


if __name__ == "__main__":
    # starts the interactive shell
    shell()

    # More test cases
    # (- (beta 2, 3))
    # (sample (- (beta 2, 3)))
    # (+ (bernoulli 1), (bernoulli 1))
    # (sample (+ (bernoulli 1_2), (bernoulli 1_2)))
    # (sample (* (bernoulli 1_2), (bernoulli 1_2)))
    # (sample (/ (bernoulli 1_2), (bernoulli 1_2)))
    # (sample (* (exponential 1_250), (normal 4, 0.1)))
    # (sample (/ (randelm (vector 100, 80, 60, 40)), (uniform 1, 20)))
    # (and true, false, false)
    # (or false, false, true)
    # (cond (true 1), (false 2))
    # (if true (+ 2, 3) (* 2, 3))
    # (let ((stop 5)) (loop smsquares ((i 0), (sm 0)) (if (= i, stop) sm (begin (print i, sm), (smsquares (+ i, 1), (+ sm, (* i, i)))))))
