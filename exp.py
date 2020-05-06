'''
This script contains our expression classes
'''
from helper import *
from env import *
from value import *

class Exp:
    '''
    The Exp class is the parent class for all types of expressions in our language
    Expressions represent the source code of our language
    '''
    def __init__(self):
        pass
    def __str__(self):
        pass
    def eval(self, env):
        pass

class EBoolean(Exp):
    '''
    EBoolean represents a boolean (true/ false) and evaluates to a VBoolean
    '''
    def __init__(self, b):
        self.val = b
    def __str__(self):
        return "EBoolean[" + str(self.val) + "]"
    def eval(self, env):
        return VBoolean(self.val)

class EString(Exp):
    '''
    EString represents a string and evaluates to a VString
    '''
    def __init__(self, s):
        self.val = s
    def __str__(self):
        return "EString[" + self.val + "]"
    def eval(self, env):
        return VString(self.val)

class ERational(Exp):
    '''
    ERational represents a fraction with a numerator and denominator and
    evaluates to a VRational
    '''
    def __init__(self, num, den):
        self.num = num
        self.den = den
    def __str__(self):
        return "ERational[" + str(self.num) + "/" + str(self.den) + "]"
    def eval(self, env):
        return VRational(self.num, self.den)

class EFloat(Exp):
    '''
    EFloat represents a float and evaluates to a VFloat
    '''
    def __init__(self, f):
        self.val = float(f)
    def __str__(self):
        return "EFloat[" + str(self.val) + "]"
    def eval(self, env):
        return VFloat(self.val)

class EPrimitive(Exp):
    '''
    EPrimitive is a wrapper for a primitive operation or python function
    and evaluates to a VPrimitive
    '''
    def __init__(self, oper):
        self.val = oper
    def __str__(self):
        return "EPrimitive[" + str(self.val) + "]"
    def eval(self, env):
        return VPrimitive(self.val)

class EIf(Exp):
    '''
    EIf represents a conditional statement and evaluates an expression
    depending on whether its ec attribute evaluates to true/false
    '''
    def __init__(self, ec, et, ee):
        self.ec = ec
        self.et = et
        self.ee = ee
    def __str__(self):
        return "EIf[" + str(self.ec) + ", " + str(self.et) + ", " + str(self.ee) + "]"
    def eval(self, env):
        ev = self.ec.eval(env)
        if ev.isBoolean():
            if not ev.getBoolean():
                return self.ee.eval(env)
            else:
                return self.et.eval(env)
        runtimeError("condition not a Boolean")

class EId(Exp):
    '''
    EId represents a variable name and lookups the value associated with its
    id when evaluated
    '''
    def __init__(self, id):
        self.id = id
    def __str__(self):
        return "EId[" + str(self.id) + "]"
    def eval(self, env):
        return env.lookup(self.id)

class EApply(Exp):
    '''
    EApply represents the application of a procedure given a series of
    arguments. It's evaluation involves evaluating the procedure expression,
    evaluating each argument expression, and then applying the arguments to the
    procedure
    '''
    def __init__(self, fn, args):
        self.fn = fn
        self.args = args
    def __str__(self):
        if len(self.args) == 0:
            return "EApply[" + str(self.fn) + "]"
        sArgs = ""
        for arg in self.args:
            sArgs += str(arg) + ", "
        return "EApply[" + str(self.fn) + ", " + sArgs[:-2] + "]"
    def eval(self, env):
        vfn = self.fn.eval(env)
        vargs = []
        for arg in self.args:
            vargs.append(arg.eval(env))
        return vfn.apply(vargs)

class EProcedure(Exp):
    '''
    EProcedure represents a procedure/ function with a name, parameters, and
    a body. It evaluates to a VProcedure
    '''
    def __init__(self, recName, params, body):
        self.recName = recName
        self.params = params
        self.body = body
    def __str__(self):
        output_str = "EProcedure[" + str(self.recName) + ", ("
        for param in self.params:
            output_str += str(param) + ", "
        output_str = output_str[:-2] + "), " + str(self.body) + "]"
        return output_str
    def eval(self, env):
        return VProcedure(self.recName, self.params, self.body, env)

class EDistribution(Exp):
    '''
    EDistribution is similar to EProcedure and represents a distribution.
    It evaluates to a VDistribution
    '''
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    def __str__(self):
        output_str = "EDistribution[" + str(self.name) + ", ("
        for param in self.params:
            output_str += str(param) + ", "
        output_str = output_str[:-2] + "), " + str(self.body) + "]"
        return output_str
    def eval(self, env):
        return VDistribution(self.name, self.params, self.body, env)

class ELoop(Exp):
    '''
    ELoop represents a loop
    '''
    def __init__(self, name, init, body):
        self.name = name
        self.init = init
        self.body = body
    def __str__(self):
        output_str = "ELoop[" + str(self.name) + ", "
        for pair in self.init:
            output_str += "(" + str(pair[0]) + ", " + str(pair[1]) + "), "
        output_str += str(self.body) + "]"
        return output_str
    def eval(self, env):
        '''
        Idea:
        - loop over the body, each time setting an environment with
          the current values of the iteration variables
        - during evaluation of the body, use an exception to iterate
          the loop
        '''
        newEnv = env
        vars = [x for x,_ in self.init]
        values = [y.eval(env) for _,y in self.init]
        while True:
            # always create a new env from the _original_ env
            newEnv = env.push(self.name, VLoop(self.name))
            for (n, v) in zip(vars, values):
                newEnv = newEnv.push(n, v)
            try:
                return self.body.eval(newEnv)
            except NextIteration as e:
                if e.name == self.name:
                    values = e.values
                else:
                    raise e
        return VBoolean(False) # to satisfy the type checker

class EMultiple(Exp):
    '''
    EMultiple takes in a list of expressions and, when evaluated, evaluates
    each expression individually and then applies an operation to the results
    '''
    def __init__(self, bodies, oper):
        self.bodies = bodies
        self.oper = oper
    def __str__(self):
        return "EMultiple[(" + ', '.join([str(body) for body in self.bodies]) + '), ' + str(self.oper) + "]"
    def eval(self, env):
        results = []
        for body in self.bodies:
            res = body.eval(env)
            # if the result is a procedure call apply to get a more refined value
            if res.isProcedure():
                res = res.apply([])
            results.append(res)
        return self.oper(results)
