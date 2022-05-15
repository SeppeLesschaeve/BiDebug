import ast
import builtins
from tokenize import String

def noop(a):
    pass

immutables = {tuple,int,float,complex,str,bytes}
class SourceVisitor(ast.NodeVisitor):

    """Class variables"""
    funcs = {}
    globals = {}
    add = lambda a,b : a + b
    sub = lambda a,b : a - b
    mul = lambda a,b : a * b
    div = lambda a,b : a / b
    en  = lambda a,b : a and b
    of  = lambda a,b : a or b
    niet = lambda a : not a
    eq  = lambda a,b : a == b
    neq = lambda a,b : a != b
    lt  = lambda a,b : a < b
    lte = lambda a,b : a <= b
    gt  = lambda a,b : a > b
    gte = lambda a,b : a >= b
    inn = lambda a,b : a in b
    nin = lambda a,b : a not in b
    iss = lambda a,b : a is b
    nis = lambda a,b : a is not b


    """Class functions"""
    def constant(s):
        try:
            return int(s)
        except ValueError:
            return None
    def getIfList(s):
        try:
            return [int(i) for i in s[1:-1].split(",")]
        except BaseException:
            return None

    """Constructor"""
    def __init__(self,bidebugger,source={}):
        self.source = source
        self.referencePool = {}
        self.returnValue = None
        self.bidebugger = bidebugger
    
    """Methods"""
    def unpack(self,v):
        """Unpacks a variable such that the return value is its actual value, not its name."""
        if isinstance(v,ast.Name):
            if v.id in self.source:
                return self.source[self.visit(v)]
            elif v.id in SourceVisitor.globals:
                return SourceVisitor.globals[self.visit(v)]
        elif isinstance(v,ast.Slice):
            step = getattr(v,"step",None)
            if not step:
                step = 1
            else:
                step = self.visit(step)
            return slice(self.visit(v.lower),self.visit(v.upper),step)
        return self.visit(v)

    def visit_Constant(self, node):
        """Returns the value contained by the node."""
        return node.value

    def visit_Name(self, node):
        """Returns the name of the variable contained by the node."""
        return node.id
    
    class Undefined:
        """A subclass to identify undefined global variables."""
        def __init__(self):
            pass
    def visit_Global(self, node):
        for name in node.names:
            SourceVisitor.globals[name] = SourceVisitor.Undefined()

    #Dit werkt niet voor assignments voor meerdere variabelen, bijv. x,y = 1,2
    def visit_Assign(self, node):
        """
        Updates source such that the new state reflects the assignments made by the node.
        Keyword arguments:
            node -- An Assignment node, containing the two relevant fields:
                targets -- a collection of all target variables of the assignment
                value   -- a value that must be assigned to the given targets
        """
        for target in node.targets:
            visitedTarget = self.visit(target)
            if isinstance(target,ast.Tuple):
                if not isinstance(node.value,ast.Tuple):
                    raise TypeError("Cannot unpack non-iterable %s object"%str(type(node.value)))
                visitedValue = self.unpack(node.value)
                if not len(visitedTarget) == len(visitedValue):
                    raise ValueError("Not enough values to unpack (expected %d, got %d)"%(len(visitedTarget),len(visitedValue)))
                for i in range(len(visitedTarget)):
                    if visitedTarget[i] not in self.source and visitedTarget[i] in SourceVisitor.globals:
                        SourceVisitor.globals[visitedTarget[i]] = visitedValue[i]
                        continue
                    self.source[visitedTarget[i]] = visitedValue[i]
                    self.bidebugger.add_state(self.copy_source())
            else:   #Nog support nodig voor target geïndexeerd met slice of index!
                    #Anders kunnen we bijv. niet a[1] = 2 of a[1:2] = [2] doen
                if visitedTarget in SourceVisitor.globals and visitedTarget not in self.source:
                    SourceVisitor.globals[visitedTarget] = self.unpack(node.value)
                else:
                    self.source[self.visit(target)] = self.unpack(node.value)
                    self.bidebugger.add_state(self.copy_source())
            self.printSource()

    def visit_Add(self, node):
        """Returns a binary addition function."""
        return SourceVisitor.add

    def visit_Sub(self, node):
        """Returns a binary subtraction function."""
        return SourceVisitor.sub

    def visit_Mult(self, node):
        """Returns a binary multiplication function."""
        return SourceVisitor.mul

    def visit_Div(self, node):
        """Returns a binary division function."""
        return SourceVisitor.div

    def visit_AugAssign(self, node):
        """
        Updates source such that the new state reflects the augmented assignment made by the node.
        Keyword arguments:
            node -- An Augmented Assignment node, containing the two relevant fields:
                target -- the targetted variable for the given augmented assignment operation
                op     -- the operation the augmented assignment is to perform on the righthand side
                value  -- the value that should be operated with the value of the target
        """
        f = self.visit(node.op)
        unpackedValue = self.unpack(node.value)
        if isinstance(node.target,ast.Name):
            visitedTarget = self.visit(node.target)
            if visitedTarget in self.source:
                self.source[visitedTarget] = f(self.source[visitedTarget],unpackedValue)
                self.bidebugger.add_state(self.copy_source())
            elif visitedTarget in SourceVisitor.globals:
                SourceVisitor.globals[visitedTarget] = f(SourceVisitor.globals[visitedTarget],unpackedValue)
        elif isinstance(node.target,ast.Subscript):
            collectionName = self.visit(node.target.value)
            if isinstance(node.target.slice,ast.Name):
                indexName = node.target.slice.id
                index = None
                if indexName in self.source or (index := SourceVisitor.constant(indexName)) or (index := SourceVisitor.getIfList(indexName)):
                    if not index:
                        index = self.source[indexName]
                elif indexName in SourceVisitor.globals:
                    index = SourceVisitor.globals[indexName]
                else:
                    raise ValueError("Index Undefined")
                if collectionName in self.source:
                    self.source[collectionName][index] = f(self.source[collectionName][index],unpackedValue)
                    self.bidebugger.add_state(self.copy_source())
                elif collectionName in SourceVisitor.globals:
                    SourceVisitor.globals[collectionName][index] = f(self.source[collectionName][index],unpackedValue)
            else:
                raise NotImplementedError("Target collection probably indexed with a slice.")
        self.printSource()
        

    def visit_Subscript(self, node):
        """Returns the slice of a collection in source that corresponds to the slice contained within the given Subscript node."""
        slce = self.unpack(node.slice)
        if node.value.id in self.source:
            return self.source[node.value.id][slce]
        elif node.value.id in self.globals:
            return self.globals[node.value.id][slce]
        val = self.unpack(node.value)
        return val[slce]

    def visit_slice(self,node):
        """Returns a slice of indices for the given Slice node."""
        return slice(node.lower,node.upper)
        #of kan ook een slice values van de lijst zelf zijn, als ik het niet juist geïnterpreteerd heb zoals het er staat,
        # maar het lijkt wel juist te zijn.

    def visit_Index(self, node):
        """Returns the value of a collection in source that corresponds to the value contained within the given Index node."""
        return self.source[self.visit(node.value)]

    #Dit werkt volgens mij niet altijd, omdat je van node.comparators enkel de laatste entry behandelt.
    # Ik zou niet weten hoe je er daar meerdere in zou kunnen steken though.
    def visit_Compare(self, node):
        """
        Returns a boolean that is true iff (node.left `operator` node.right) is satisfied.
        Keyword arguments:
            node -- A Compare node, containing the three relevant fields:
                left        -- A node containing the lefthand side of the comparison
                comparators -- A collection of righthand sides for the comparison
                ops         -- A collection of comparator operators for the comparison
        Returns:
            the result of the comparison.
        """
        lefthand = self.unpack(node.left)
        comps = [lefthand]
        for c in node.comparators:
            temp = self.unpack(c)
            comps.append(temp)
        fs = []
        for o in node.ops:
            fs.append(self.visit(o))
        b = fs[0](comps[0],comps[1])
        for i in range(1,len(fs)):
            b = fs[i](b,comps[i])
        return b

    def visit_Eq(self, node):
        """Returns a binary equality function."""
        return SourceVisitor.eq

    def visit_NotEq(self, node):
        """Returns a binary inequality function."""
        return SourceVisitor.neq

    def visit_Lt(self, node):
        """Returns a binary less-than function."""
        return SourceVisitor.lt

    def visit_LtE(self, node):
        """Returns a binary less-than-or-equal-to function."""
        return SourceVisitor.lte

    def visit_Gt(self, node):
        """Returns a binary greater-than function."""
        return SourceVisitor.gt

    def visit_GtE(self, node):
        """Returns a binary greater-than-or-equal-to function."""
        return SourceVisitor.gte

    def visit_List(self, node):
        """
        Returns the list corresponding to the list referenced in the node object.
        Keyword arguments:
        node -- A List node object, containing the relevant field:
            elts -- the elements of the list referenced by the node
        Returns:
            the evaluated list referenced by the node
        """
        elements = []
        for element in node.elts:
            elements.append(self.visit(element))
        return elements

    def visit_Tuple(self, node):
        """Returns a tuple in accordance with node."""
        l = []
        if isinstance(node.ctx,ast.Store):
            for el in node.elts:
                l.append(self.visit(el))
            return tuple(l)
        for el in node.elts:
            l.append(self.unpack(el))
        return tuple(l)

    def visit_In(self, node):
        """Returns a binary in operation."""
        return SourceVisitor.inn

    def visit_NotIn(self, node):
        """Returns a binary not-in operation."""
        return SourceVisitor.nin

    def visit_IsNot(self, node):
        """Returns a binary is-not operation."""
        return SourceVisitor.nis

    def visit_Is(self, node):
        """Returns a binary is operation."""
        return SourceVisitor.iss

    def visit_Expr(self, node):
        """Visits the expression contained by the node."""
        self.visit(node.value)

    def visit_UnaryOp(self, node):
        return self.visit(node.op)(self.visit(node.operand))
    
    def visit_UAdd(self, node):
        return lambda a: 0+a
    
    def visit_USub(self, node):
        return lambda a: 0-a
    
    def visit_Not(self, node):
        return lambda a: not a
    
    def visit_Invert(self,node):
        return lambda a: ~a

    def visit_BinOp(self, node):
        """Visits the binary operation contained by the node."""
        lefthand = self.unpack(node.left)
        righthand = self.unpack(node.right)
        f = self.visit(node.op)
        op = node.op
        return f(lefthand,righthand)

    def visit_If(self, node):
        """
        Evaluates an If node and visits the relevant parts of the code.
        Keyword arguments:
        node -- An If node, containing the three relevant fields:
            test   -- a Compare node containing the test for the if-expression
            body   -- an Expr node containing the body of code that is to be executed if the test succeeds
            orelse -- an Expr node containing the body of code that is to be executed if the test fails
        """
        if self.visit(node.test):
            for n in node.body:
                self.visit(n)
        elif node.orelse:
            for n in node.orelse:
                self.visit(n)

    def visit_BoolOp(self, node):
        """Visits the boolean operation contained within the node."""
        if len(node.values) != 2:
            raise RuntimeError("Boolean op did not receive exactly 2 arguments")
        lefthand = self.unpack(node.values[0])
        righthand = self.unpack(node.values[1])
        f = self.visit(node.op)
        return f(lefthand,righthand)

    def visit_And(self, node):
        """Returns a binary and function."""
        return SourceVisitor.en

    def visit_Or(self, node):
        """Returns a binary or function."""
        return SourceVisitor.of
    
    def visit_Not(self, node):
        return SourceVisitor.niet

    def visit_While(self, node):
        """
        Visits the relevant body of code while the while test is satisfied.
        Keyword arguments:
            node -- A While node, containing the two relevant fields:
                test -- a Compare node that corresponds to the test for the while loop
                body -- an Expr node that corresponds to the code within the while loop
        """
        while self.visit(node.test):
            for n in node.body:
                self.visit(n)
            for n in node.orelse:
                self.visit(n)

    def visit_FunctionDef(self, node):
        """
        Adds the function defined by the node to source to reflect its definition.
        Keyword arguments:
            node -- A FunctionDef node, containing the two relevant fields:
                body -- the body of code of the function to be defined
                args -- an object containing a collection of arguments, containing:
                    args -- a collection of arguments for the function that is to be defined
        """
        SourceVisitor.funcs[node.name] = []
        funcn = SourceVisitor.funcs[node.name]
        arguments = []
        if isinstance(node.args.args, list):
            for argument in node.args.args:
                if isinstance(argument, ast.arg):
                    arguments.append(argument.arg)
        funcn.append(arguments)
        funcn.append([])
        for i in range(len(node.body)):
            funcn[1].append(node.body[i])
        self.printSource()

    def visit_Call(self, node):
        """
        Visits a call to a given function.
        Keyword arguments:
            node -- A Call node, containing the two relevant fields:
                func -- an Expr node, containing the relevant field:
                    id -- the name of the function to be called
                args -- the arguments to the function, processed in updateReferencePoolFromCall
        """
        if self.isBuiltin(node):
            return self.visit_Builtin(node)
        #print("function call: %s"%(node.func.id))
        
        self.makeReferencePool(node)
        ts = self.buildTempSource(node)
        funcenv = SourceVisitor(self.bidebugger,ts)
        for statement in SourceVisitor.funcs[node.func.id][1]:
            funcenv.visit(statement)
            if funcenv.returnValue != None:
                funcenv.source["returned"] = funcenv.returnValue
                self.bidebugger.add_state(funcenv.source)
                break
        for key in self.referencePool:
            self.source[self.referencePool[key]] = funcenv.source[key]
        #print("return from: %s"%(node.func.id))
        return funcenv.returnValue
        

    def is_immutable(self, obj):
        """Returns whether an abject is immutable."""
        return type(obj) in immutables

    def visit_Return(self, node):
        """Visits a return statement and assigns its evaluated value to the class' return value field."""
        self.returnValue = self.unpack(node.value)

    #The iterator must be a deep copy of the associated element of the list.
    def visit_For(self, node):
        """
        Visits the relevant body for all elements in the collection over which the for loop iterates.
        Keyword arguments:
            node -- A For node, containing the three relevant fields:
                iter   -- an Iter node containing the collection over which the for loop is to iterate
                target -- the target variable used as iterator in the for loop
                body   -- an Expr node that corresponds to the code within the while loop
        """
        if isinstance(node.iter, ast.Name):
            listLabel = self.visit(node.iter)
            for element in self.source[listLabel]:
                self.source[self.visit(node.target)] = element
                for n in node.body:
                    self.visit(n)
                    element = self.source[self.visit(node.target)]
        elif isinstance(node.iter, ast.Call):
            for j in self.visit(node.iter):
                self.source[node.target.id] = j
                for n in node.body:
                    self.visit(n)
        for n in node.orelse:
            self.visit(n)

    def visit_Expr(self, node):
        """Visits the given Expression."""
        self.visit(node.value)

    def visit_Builtin(self, node):
        """
        Visits the given built-in function.
        Keyword arguments:
            node -- A Call node object, containing the two relevant fields:
                args -- a collection of arguments to the function
                func -- a FunctionDef node containing the built-in function to be evaluated
        """
        arguments = []
        for arg in node.args:
            arguments.append(self.unpack(arg))
        if isinstance(node.func,ast.Name) and node.func.id == "print":
            return noop(*arguments)
        if isinstance(node.func, ast.Attribute):    #Dit valt voor wanneer de functie opgeroepen wordt op een object
            if node.func.value.id in self.source:
                return getattr(self.source[self.visit(node.func.value)], node.func.attr)(*arguments)
            elif node.func.value.id in SourceVisitor.globals:
                return getattr(SourceVisitor.globals[node.func.value.id], node.func.attr)(*arguments)
        if isinstance(node.func, ast.Name):
            return getattr(builtins, node.func.id)(*arguments)

    def buildTempSource(self, node):
        """
        Builds and returns a temporary source from our current source that encompasses only those entries that the node would need to see.
        Those entries would be the function argument, globals (currently not supported) and function definitions.
        Keyword arguments:
            node -- a Call node, containing the _ relevant fields:
                func -- a name object for the function, containing the relevant field
                    id -- the name of the function
                args -- the arguments to the function
        """
        tempSource = {}
        argnames = SourceVisitor.funcs[node.func.id][0]
        if isinstance(node.args, list):
            for i in range(0, len(node.args)):
                visitedArg = self.visit(node.args[i])
                if isinstance(visitedArg,str) and visitedArg in self.source:
                    tempSource[argnames[i]] = self.source[visitedArg]
                else:
                    tempSource[argnames[i]] = visitedArg
        for j in range(0, len(node.keywords)):
            if self.visit(node.keywords[j].value) in self.source:
                tempSource[node.keywords[j].arg] = self.source[self.visit(node.keywords[j].value)]
            else:
                tempSource[node.keywords[j].arg] = self.visit(node.keywords[j].value)
        #self.addAllFunctions(tempSource)
        return tempSource

    def addAllFunctions(self,tempSource):
        """Adds all functions in source to the given temporary source."""
        for f in self.source:
            if self.isFunction(f):
                tempSource[f] = self.source[f]
    
    def isFunction(self,f):
        """Checks if the given node is a function defined in source."""
        if not isinstance(self.source[f],list):
            return False
        if not isinstance(self.source[f][1],list):
            return False
        return isinstance(self.source[f][1][0],ast.Expr)   #Niet zeker of dit niet simpeler kan, of zelfs of dit volledig juist is.

    def makeReferencePool(self,node):
        """
        Constructs a reference pool for mutables in a function call as follows:
            {function_parameter : source_variable}
        This is structured this way so that the keys are unique,
        even if a variable is passed to multiple different function parameters.
        Key arguments:
            node -- A Call object containing the following two relevant fields:
                keywords -- a list of keyword arguments to the function call
                args     -- a list of arguments to the function call, containing the following two relevant field:
                    arg   -- the id for the argument as seen by the function itself, the function parameter name
                    value -- the id for the argument as seen by source, the caller argument
        """
        references = {}
        if not isinstance(node.args,list):
            raise RuntimeError("Incorrect function call: arguments are not in a list.")
        for i,arg in enumerate(node.args):
            visitedArg = self.visit(arg)
            if isinstance(visitedArg,str) and visitedArg in self.source and not self.is_immutable(self.source[visitedArg]):
                references[SourceVisitor.funcs[node.func.id][0][i]] = visitedArg
        for arg in node.keywords:
            references[arg.arg] = self.visit(arg.value)
        self.referencePool = references

    def isBuiltin(self, node):
        """Returns a boolean indicating whether a function is a built-in."""
        return isinstance(node.func, ast.Attribute) \
               or (isinstance(node.func, ast.Name) and not SourceVisitor.funcs.get(node.func.id,False))

    def printSource(self):
        """pSource = {}
        for entry in self.source:
            pSource[entry] = self.source[entry]
        for entry in SourceVisitor.globals:
            if isinstance(SourceVisitor.globals[entry],SourceVisitor.Undefined):
                pSource[entry] = "Undefined"
                continue
            pSource[entry] = SourceVisitor.globals[entry]
        for f in SourceVisitor.funcs:
            pSource[f] = (len(SourceVisitor.funcs[f][0]),len(SourceVisitor.funcs[f][1]))
        print(pSource)"""
        pass
    
    def copy_source(self):
        return dict(self.source)

"""def main(source):
    tree = ast.parse(source)
    #print(ast.dump(tree))
    usage_analyzer = SourceVisitor()
    usage_analyzer.visit(tree)
    #print(usage_analyzer.source)"""


if __name__ == '__main__':
    text = """
def fibonacci(n):
    fib = [1,1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib[-1]
print(fibonnaci(3))
"""
    simpel_voorbeeld = """
a = 1
a = a + 1"""
    #main(text)
