'''
This script contains our parse and parser transformations
'''
from helper import *
from exp import *
from value import *
from env import *
from parsita import *
from parsita.util import constant
import string
import random

LP = reg(r'([ ]*)\(([ ]*)')
RP = reg(r'([ ]*)\)([ ]*)')

def gensym():
    '''
    Generate a random sequence of characters
    '''
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))

def mkCond(conditions):
    '''
    A parser transformation for conditions (a series of conditionals)
    '''
    conditions_rev = conditions[::-1]
    result = EIf(conditions_rev[0][0], conditions_rev[0][1], EBoolean(False))
    for e in conditions_rev[1:]:
        result = EIf(e[0], e[1], result)
    return result

def mkBegin(es):
    '''
    A parser transformation for begin (a series of expressions to evaluate
    sequentially)
    '''
    if len(es) < 1:
        return EBoolean(False)
    ess = es[::-1]
    result = ess[0]
    for e in ess[1:]:
        result = mkLet([(gensym(), e)], result)
    return result

def mkLet(bindings, e2):
    '''
    A parser transformation for let (used to locally define a variable)
    '''
    strs = []
    exprs = []
    for binding in bindings:
        strs.append(binding[0])
        exprs.append(binding[1])
    return EApply(EProcedure(gensym(), strs, e2), exprs)

def mkAnd(es):
    '''
    A parser transformation for the boolean operation, and
    '''
    if len(es) < 1:
        return EBoolean(True)
    ess = es[::-1]
    result = EIf(ess[0], EBoolean(True), EBoolean(False))
    for e in ess[1:]:
        result = EIf(e, result, EBoolean(False))
    return result

def mkOr(es):
    '''
    A parser transformation for the boolean operation, or
    '''
    if len(es) < 1:
        return EBoolean(False)
    ess = es[::-1]
    result = EIf(ess[0], EBoolean(True), EBoolean(False))
    for e in ess[1:]:
        result = EIf(e, EBoolean(True), result)
    return result

class AtomicParser(TextParsers):
    '''
    AtomicParser contains all of the parsers that match a sequence of tokens
    to an atomic expression, returning an abstract representation of what was matched
    '''
    atomic_float = reg(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][-+]?[0-9]+)?') > (lambda x: EFloat(float(x)))
    integer = reg(r'[-+]?[0-9]+') > int
    atomic_id = reg(r"""[a-zA-Z_*+~%=>^</?-][a-zA-Z0-9_*+~%=>^</?-]*""") > (lambda x: EId(x))
    atomic_rational = integer << lit('_') & integer > (lambda x: ERational(x[0], x[1]))
    atomic_string = reg(r"""\"[^"]*\"""") > (lambda x: EString(str(x[1:-1])))
    atomic_true = lit('true') > (lambda x: EBoolean(True)) #EBoolean[True]
    atomic_false = lit('false') > (lambda x: EBoolean(False))
    atomic = atomic_rational | atomic_float | atomic_true | atomic_false | atomic_id | atomic_string

class ExpParser(TextParsers):
    '''
    ExpParser contains all of the parsers that match a sequence of tokens
    to an expression (including atomic expressions), returning an abstract
    representation of what was matched.
    '''
    atomic = AtomicParser.atomic
    id = reg(r"""[a-zA-Z_*+=</?-][a-zA-Z0-9_*+=</?-]*""")
    bindings_one = LP >> id & expr << RP > (lambda x: (x[0], x[1]))
    bindings = repsep(bindings_one, ', ')
    params_one = reg(r'[ ]*') >> id > str
    params = repsep(params_one, ', ')
    conditions_one = LP >> expr & expr << RP > (lambda x: (x[0], x[1]))
    conditions = repsep(conditions_one, ', ')
    expr_if = LP >> lit('if') >> expr & reg(r'[ ]*') >> expr & reg(r'[ ]*') >> expr << RP > (lambda x: EIf(x[0], x[1], x[2]))
    expr_let = LP >> lit('let') >> LP >> bindings & RP >> expr << RP > (lambda x: mkLet(x[0], x[1]))
    expr_fun = LP >> lit('lambda') >> LP >> params << RP & expr << RP > (lambda x: EProcedure(gensym() , x[0], x[1]))
    expr_rec_fun = LP >> lit('lambda') >> id & LP >> params << RP & expr << RP > (lambda x: EProcedure(x[0], x[1], x[2]))
    expr_dist = LP >> lit('defdist') >> LP >> id & reg(r'[ ]*') >> params << RP & expr << RP > (lambda x: EDistribution(x[0], x[1], x[2]))
    expr_apply = LP >> expr & reg(r'[ ]*') >> exprs << RP > (lambda x: EApply(x[0], x[1]))
    expr_cond = LP >> lit('cond') >> conditions << RP > (lambda x: mkCond(x))
    expr_do = LP >> lit('begin') >> exprs << RP > (lambda x: mkBegin(x))
    expr_and = LP >> lit('and') >> exprs << RP > (lambda x: mkAnd(x))
    expr_or = LP >> lit('or') >> exprs << RP > (lambda x: mkOr(x))
    expr_loop = LP >> lit('loop') >> id & LP >> bindings & RP >> expr << RP > (lambda x: ELoop(x[0], x[1], x[2]))
    expr = atomic | expr_if | expr_let| expr_loop | expr_dist | expr_fun | expr_rec_fun | expr_do | expr_and | expr_or | expr_cond | expr_apply
    exprs = repsep(expr, ', ')

def parse(input):
    '''
    Parse an input and returns its abstract representation.
    If there is no match, it raises a parsing error
    '''
    try:
        return ExpParser.expr.parse(input).value
    except Exception as e:
        runtimeError("Cannot parse "+input+": "+str(e))

if __name__ == "__main__":
    # Some parsing test functions
    print(ExpParser.expr.parse('(let ((var1 true), (var2 false)) var1)').value, '\n')
    print(ExpParser.expr.parse('(lambda (val1, val2) true)').value, '\n')
    print(ExpParser.expr.parse('(cond (false 1), (true 2))').value, '\n')
    print(ExpParser.expr.parse('(begin true, false)').value, '\n')
    print(ExpParser.expr.parse('(and true, false)').value, '\n')
    print(ExpParser.expr.parse('(or true, false)').value, '\n')
    print(ExpParser.expr.parse('(lambda (a, b) (* a, a))').value, '\n')
    print(ExpParser.expr.parse('(if true (+ 2, 3) (* 2, 3))').value, '\n')
    print(ExpParser.expr.parse('(let ((stop 10000)) (loop sum-squares ((i 0), (sum 0)) (if (= i, stop) sum (do (print i, sum), (sum-squares (+ i, 1), (+ sum, (* i, i)))))))').value, '\n')
