import ast


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
    def __init__(self,tree,source={},breakpoints=set()):
        self.tree = tree
        self.source = source
        self.referencePool = {}
        self.returnValue = None
        self.breakpoints = SourceVisitor.fbps(breakpoints,tree)
    
    def fbps(bpts,tree):
        breakpoints = set()
        l = SourceVisitor.flatten(tree)
        for bpno in bpts:
            breakpoints.add(l[bpno])
        return breakpoints

    def flatten(tree):
        if not getattr(tree,"body",None):
            return [tree]
        l = [tree]
        if getattr(tree,"test",None):
            l += SourceVisitor.flatten(tree.test)
        for node in tree.body:
            l += SourceVisitor.flatten(node)
        if not getattr(tree,"orelse",None):
            return l
        for node in tree.orelse:
            l += SourceVisitor.flatten(node)
        return l
    
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
                if visitedArg in self.source:
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


    def isBreakPoint(self,node):
        return node in self.breakpoints

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
            if visitedArg in self.source and not self.is_immutable(self.source[visitedArg]):
                references[SourceVisitor.funcs[node.func.id][0][i]] = visitedArg
        for arg in node.keywords:
            references[arg.arg] = self.visit(arg.value)
        self.referencePool = references

    def isBuiltin(self, node):
        """Returns a boolean indicating whether a function is a built-in."""
        return isinstance(node.func, ast.Attribute) \
               or (isinstance(node.func, ast.Name) and not SourceVisitor.funcs.get(node.func.id,False))

    def printSource(self):
        pSource = {}
        for entry in self.source:
            pSource[entry] = self.source[entry]
        for entry in SourceVisitor.globals:
            if isinstance(SourceVisitor.globals[entry],SourceVisitor.Undefined):
                pSource[entry] = "Undefined"
                continue
            pSource[entry] = SourceVisitor.globals[entry]
        for f in SourceVisitor.funcs:
            pSource[f] = (len(SourceVisitor.funcs[f][0]),len(SourceVisitor.funcs[f][1]))
        print(pSource)

def main(source):
    tree = ast.parse(source)
    l = SourceVisitor.flatten(tree)
    print(l)
    s = SourceVisitor(tree,{},{1,2,3})
    print(s.breakpoints)
    #print(ast.dump(tree))
    #usage_analyzer = SourceVisitor(tree)
    #usage_analyzer.visit(tree)
    #print(usage_analyzer.source)


if __name__ == '__main__':
    text = """
a = [1,2,3,4,5]
b = a[1:3]
for i in range(len(b)):
    b[i] += 1
for i in range(a[1:3]):
    i = 1
print(a)
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
