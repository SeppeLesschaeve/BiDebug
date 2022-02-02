import ast
import builtins

immutables = {tuple,int,float,complex,str,bytes}
class SourceVisitor(ast.NodeVisitor):

    def __init__(self,source={}):
        self.source = source
        self.referencePool = {}
        self.returnValue = None

    def unpack(self,v):
        if isinstance(v,ast.Name):
            return self.source[self.visit(v)]
        return self.visit(v)

    def visit_Constant(self, node):
        """Returns the value contained by the node."""
        return node.value

    def visit_Name(self, node):
        """Returns the name of the variable contained by the node."""
        return node.id

    #Werkt dit voor bijv. "x,y = 1,2"?
    def visit_Assign(self, node):
        """
        Updates source such that the new state reflects the assignments made by the node.
        Keyword arguments:
            node -- An Assignment node, containing the two relevant fields:
                targets -- a collection of all target variables of the assignment
                value   -- a value that must be assigned to the given targets
        """
        for target in node.targets:
            self.source[self.visit(target)] = self.unpack(node.value)
            #self.updateAll(self.visit(target)) moet volgens mij niet, omdat we werken met references, niet values.
            print(self.source)

    # welke op we moeten doen en die daar dan uitvoeren of met een functie afhandelen.
    def visit_Add(self, node):
        """Returns a binary addition function."""
        return lambda a,b : a + b

    def visit_Sub(self, node):
        """Returns a binary subtraction function."""
        return lambda a,b : a - b

    def visit_Mult(self, node):
        """Returns a binary multiplication function."""
        return lambda a,b : a * b

    def visit_Div(self, node):
        """Returns a binary division function."""
        return lambda a,b : a / b

    def visit_AugAssign(self, node):
        """
        Updates source such that the new state reflects the augmented assignment made by the node.
        Keyword arguments:
            node -- An Augmented Assignment node, containing the two relevant fields:
                target -- the targetted variable for the given augmented assignment operation
                op     -- the operation the augmented assignment is to perform on the righthand side
                value  -- the value that should be operated with the value of the target
        """
        visitedTarget = self.visit(node.target)
        unpackedValue = self.unpack(node.value)
        f = self.visit(node.op)
        if visitedTarget in self.source:
            self.source[visitedTarget] = f(self.source[visitedTarget],unpackedValue)
        #if self.visit(node.target) in self.source:
        #    self.source[self.visit(node.target)] = self.visit(node.op)
        #    self.updateAll(self.visit(node.target))
        #elif isinstance(node.target, ast.Subscript):
        #    self.source[self.visit(node.target.value)][self.visit(node.target.slice)] = self.visit(node.op)
        #    self.updateAll(self.visit(node.target.value))
        print(self.source)

    def visit_Subscript(self, node):
        """Returns the slice of a collection in source that corresponds to the slice contained within the given Subscript node."""
        slce = self.unpack(node.slice)
        val = self.unpack(node.value)
        return val[slce]

    def visit_slice(self,node):
        """Returns a slice of indices for the given Slice node."""
        return range(node.lower,node.upper)
        #of kan ook een slice values van de lijst zelf zijn, als ik het niet juist geïnterpreteerd heb zoals het er staat

    #Is deprecated volgens de docs
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
        return lambda a,b : a == b

    def visit_NotEq(self, node):
        """Returns a binary inequality function."""
        return lambda a,b : a != b

    def visit_Lt(self, node):
        """Returns a binary less-than function."""
        return lambda a,b : a < b

    def visit_LtE(self, node):
        """Returns a binary less-than-or-equal-to function."""
        return lambda a,b : a <= b

    def visit_Gt(self, node):
        """Returns a binary greater-than function."""
        return lambda a,b : a > b

    def visit_GtE(self, node):
        """Returns a binary greater-than-or-equal-to function."""
        return lambda a,b : a >= b

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

    def visit_In(self, node):
        """Returns a binary in operation."""
        return lambda a,b : a in b

    def visit_NotIn(self, node):
        """Returns a binary not-in operation."""
        return lambda a,b : a not in b

    def visit_IsNot(self, node):
        """Returns a binary is-not operation."""
        return lambda a,b : a is not b

    def visit_Is(self, node):
        """Returns a binary is operation."""
        return lambda a,b : a is b

    def visit_Expr(self, node):
        """Visits the expression contained by the node."""
        self.visit(node.value)

    def visit_BinOp(self, node):
        """Visits the binary operation contained by the node."""
        lefthand = self.unpack(node.left)
        righthand = self.unpack(node.right)
        f = self.visit(node.op)
        op = node.op
        return f(lefthand,righthand)
        #return self.visit(node.op)

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
        return lambda a,b : a and b

    def visit_Or(self, node):
        """Returns a binary or function."""
        return lambda a,b : a or b

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

    def visit_FunctionDef(self, node):
        """
        Adds the function defined by the node to source to reflect its definition.
        Keyword arguments:
            node -- A FunctionDef node, containing the two relevant fields:
                body -- the body of code of the function to be defined
                args -- an object containing a collection of arguments, containing:
                    args -- a collection of arguments for the function that is to be defined
        """
        self.source[node.name] = []
        arguments = []
        if isinstance(node.args.args, list):
            for argument in node.args.args:
                if isinstance(argument, ast.arg):
                    arguments.append(argument.arg)
        self.source[node.name].append(arguments)
        self.source[node.name].append(node.body[0])
        print(self.source)

    #Hier gaan we nog iets moeten returnen als het laatste argument een return command is.
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
        self.makeReferencePool(node)
        #self.updateReferencePoolFromCall(node)
        ts = self.buildTempSource(node)
        funcenv = SourceVisitor(ts)
        funcenv.visit(ts[node.func.id][1])
        for key in self.referencePool:
            self.source[self.referencePool[key]] = funcenv.source[key]
        return funcenv.returnValue
        

    def is_immutable(self, obj):
        """Returns whether an abject is immutable."""
        return type(obj) in immutables

    def visit_Return(self, node):
        self.returnValue = self.visit(node.value)

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
            for i in range(0, len(self.source[listLabel])):
                temp = self.source[listLabel][i]
                self.source[self.visit(node.target)] = temp
                for n in node.body:
                    self.visit(n)
                    self.source[listLabel][i] = self.source[self.visit(node.target)]
        if isinstance(node.iter, ast.Call):
            for j in self.visit(node.iter):
                self.source[node.target.id] = j
                for n in node.body:
                    self.visit(n)
        self.source.pop(node.target.id)

    def visit_Expr(self, node):
        """Visits the given Expression."""
        self.visit(node.value)

    #Ook hier moeten we iets returnen als het laatste command van de functie een return call is.
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
            visitedArg = self.visit(arg)
            if visitedArg in self.source:
                arguments.append(self.source[visitedArg])
            else:
                arguments.append(visitedArg)
        if isinstance(node.func, ast.Attribute):
            getattr(self.source[self.visit(node.func.value)], node.func.attr)(*arguments)
        if isinstance(node.func, ast.Name):
            return getattr(builtins, node.func.id)(*arguments)

    #We moeten hier ook nog function definitions en zo aan de temporary source toevoegen.
    def buildTempSource(self, node):
        """
        Builds and returns a temporary source from our current source that encompasses only those entries that the node would need to see.
        Keyword arguments:
            node -- a Call node, containing the _ relevant fields:
                func -- a name object for the function, containing the relevant field
                    id -- the name of the function
                args -- the arguments to the function
        """
        tempSource = {}
        argnames = self.source[node.func.id][0]
        if isinstance(node.args, list):
            for i in range(0, len(node.args)):
                visitedArg = self.visit(node.args[i])
                if visitedArg in self.source:
                    tempSource[argnames[i]] = self.source[visitedArg]
                else:
                    tempSource[argnames[i]] = visitedArg
        for j in range(0, len(node.keywords)):
            if self.visit(node.keywords[j].value) in self.source:
                tempSource[node.keywords[j].arg] = self.source[self.visit(node.keywords[j].value)]
            else:
                tempSource[node.keywords[j].arg] = self.visit(node.keywords[j].value)
        self.addAllFunctions(tempSource)
        return tempSource

    def addAllFunctions(self,tempSource):
        for f in self.source:
            if self.isFunction(f):
                tempSource[f] = self.source[f]
    
    def isFunction(self,f):
        if not isinstance(self.source[f],list):
            return False
        return isinstance(self.source[f][1],ast.Return) or isinstance(self.source[f][1],ast.Expr)   #Niet zeker of dit niet simpeler kan

    #Moeten we dit wel doen als we alleen maar call-by-reference gebruiken voor collections (en evt. objects)?
    #Volgens mij werkt deze methode trouwens niet voor nested function calls.
    # self.referencepool gaat dan namelijk overschreven worden op elk nieuw niveau.
    def updateAll(self, updated_reference):
        """Updates all references to an updated value."""
        updated_value = self.source[updated_reference]
        for key in self.referencePool:
            if updated_reference in self.referencePool[key]:
                for reference in self.referencePool[key]:
                    if reference is not updated_reference:  #Mogen we dit niet gewoon vervangen door de body van deze if-statement?
                        self.source[reference] = updated_value

    def makeReferencePool(self,node):
        references = {}
        if not isinstance(node.args,list):
            raise RuntimeError("Incorrect function call: arguments are not in a list.")
        for i,arg in enumerate(node.args):
            visitedArg = self.visit(arg)
            if visitedArg in self.source and not self.is_immutable(self.source[visitedArg]):
                references[self.source[node.func.id][0][i]] = visitedArg
        for arg in node.keywords:
            references[arg.arg] = self.visit(arg.value)
        self.referencePool = references

def main(source):
    tree = ast.parse(source)
    #print(ast.dump(tree))
    usage_analyzer = SourceVisitor()
    usage_analyzer.visit(tree)
    #print(usage_analyzer.source)


if __name__ == '__main__':
    text = """
def test(a, b, l):
    a.append(1)
    b += 1
    c = 1 + b 
    l.append(c)
    l.pop()
    l.sort()
    if 1 in l:
        l.append(1)
    d = range(0, len(l))
    
    
a = 2
b = 4
ll = [1, 2, 3, 4]
if (a * 2 >= 4) and (1 > a or b > 3):
    c = 2
    while c > 0:
        c -= 1
else:
    for i in range(0, len(ll)):
        ll[i] *= ll[i]
    for i in ll:
        i /= i
    else:
        b += 1
if (a * 2 >= 4) and (1 > a or b > 3):
    for i in range(0, len(ll)):
        ll[i] *= ll[i]
    for i in ll:
        i = 2
    else:
        b += 1
else:
    c = 2
    while c > 0:
        c -= 1
a = 4
b += a
test(ll, l = ll, b = 1)
print(a,b,c,i,ll)
"""
    main(text)
