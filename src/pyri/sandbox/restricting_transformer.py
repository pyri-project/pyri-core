from RestrictedPython.transformer import RestrictingNodeTransformer, ALLOWED_FUNC_NAMES, copy_locations
import ast

class PyriRestrictingNodeTransformer(RestrictingNodeTransformer):
    def __init__(self, errors=None, warnings=None):
        super().__init__(errors,warnings)

        self.print_info.printed_used=True
        self.print_info.print_used=True
        
        self.special_functions = ["_begin_blockly_statement_","_end_blockly_statement_"]

    def check_name(self, node, name, allow_magic_methods=False):
        super().check_name(node,name,allow_magic_methods)
        if name is None:
            return
        if (name.endswith('_') or name.startswith('_')):
            self.error(
                node,
                '"{name}" is an invalid variable name because it '
                'starts or ends with "_"'.format(name=name))

    # Variables

    def visit_Name(self, node):
        """
        PyRI names must not end with underscore
        """

        #Functionality moved to check_name()

        return super().visit_Name(node)
    
    # Variables

    def visit_Starred(self,node):
        """
        Starred operator is denied in PyRI
        """
        self.not_allowed(node)

    # Expressions

    def check_return_value(self,node,ret_node):
        new_node = ast.Call(
            func=ast.Name('_check_return_', ast.Load()),
            args=[ret_node],
            keywords=[]
        )
        copy_locations(new_node, node)
        return new_node

    def check_unary_op_allowed(self,node,ret_node):
        new_node = ast.Call(
            func=ast.Name('_check_unary_op_allowed_', ast.Load()),
            args=[ret_node],
            keywords=[]
        )
        copy_locations(new_node, node)
        return new_node

    def visit_UnaryOp(self,node):
        """
        Wrap return in _check_return_ to check for unwrapped objects
        """
        
        ret_node = super().visit_UnaryOp(node)
        operand1 = ast.Call(
            func=ast.Name('_check_unary_op_allowed_', ast.Load()),
            args=[ret_node.operand],
            keywords=[]
        )
        copy_locations(operand1, ret_node.operand)
        ret_node.operand = operand1
        return self.check_return_value(node,ret_node)

    def visit_BinOp(self,node):
        """
        Wrap return in _check_return_ to check for unwrapped objects
        """
        
        ret_node = super().visit_BinOp(node)
        left1 = ast.Call(
            func=ast.Name('_check_binary_op_allowed_', ast.Load()),
            args=[ret_node.left],
            keywords=[]
        )
        right1 = ast.Call(
            func=ast.Name('_check_binary_op_allowed_', ast.Load()),
            args=[ret_node.right],
            keywords=[]
        )
        copy_locations(left1, ret_node.left)
        copy_locations(right1, ret_node.right)
        ret_node.left = left1
        ret_node.right = right1
        return self.check_return_value(node,ret_node)

    def visit_BoolOp(self,node):
        """
        Wrap return in _check_return_ to check for unwrapped objects
        """
        
        ret_node = super().visit_BoolOp(node)
        values1 = []
        for v in ret_node.values:             
            f = ast.Call(
                func=ast.Name('_check_bool_op_allowed_', ast.Load()),
                args=[v],
                keywords=[])
            values1.append(f)
            copy_locations(f, v)
             
        ret_node.values = values1
        return self.check_return_value(node,ret_node)

    def visit_Compare(self,node):
        """
        Wrap return in _check_return_ to check for unwrapped objects
        """
        
        ret_node = super().visit_Compare(node)
        left1 = ast.Call(
            func=ast.Name('_check_compare_allowed_', ast.Load()),
            args=[ret_node.left],
            keywords=[]
        )
        copy_locations(left1,ret_node.left)

        comparators1 = []
        for v in ret_node.comparators:
            
            f = ast.Call(
                func=ast.Name('_check_compare_allowed_', ast.Load()),
                args=[v],
                keywords=[]
                )
            copy_locations(f, v)
            comparators1.append(f)
        
        ret_node.left = left1
        ret_node.comparators = comparators1

        return self.check_return_value(node,ret_node)

    def visit_MatMult(self,node):
        """
        MatMult is denied in RestrictedPython. Allow in PyRI
        """
        return self.node_contents_visit(node)

    def visit_Call(self,node):
        """
        Modify Call to allow for calling special functions
        Wrap return in _check_return_ to check for unwrapped objects
        """

        # TODO: protect against overwritting builtins and plugins

        special_function = False

        for keyword_arg in node.keywords:
            if keyword_arg.arg is None:
                self.error(node, '**kwargs is not allowed.')

        if isinstance(node.func, ast.Name):
            if node.func.id == 'exec':
                self.error(node, 'Exec calls are not allowed.')
            elif node.func.id == 'eval':
                self.error(node, 'Eval calls are not allowed.')

            if node.func.id in self.special_functions:
                special_function = True

        if not special_function:
            ret_node = super().visit_Call(node)        
            return self.check_return_value(node,ret_node)

        # Temporarily change name so name checks are passed
        old_func_id = node.func.id
        node.func.id = "special_placeholder"
        ret_node = super.visit_Call(node)
        ret_node.func.id = old_func_id

        return self.check_return_value(node,ret_node)

    def visit_Attribute(self,node):
        """
        Wrap return in _check_return_ to check for unwrapped objects
        """
        
        ret_node = super().visit_Attribute(node)
        if (isinstance(node.ctx,ast.Load)):
            return self.check_return_value(node,ret_node)
        else:
            return ret_node

    # Subscripting

    def visit_Subscript(self,node):
        """
        Wrap return in _check_return_ to check for unwrapped objects
        """
        
        ret_node = super().visit_Subscript(node)
        if (isinstance(node.ctx,ast.Load)):
            return self.check_return_value(node,ret_node)
        else:
            return ret_node

    


    # Comprehensions

    def visit_ListComp(self,node):
        """
        Comprehensions are not allowed in PyRI to reduce complexity
        """
        self.not_allowed(node)

    def visit_SetComp(self,node):
        """
        Comprehensions are not allowed in PyRI to reduce complexity
        """
        self.not_allowed(node)

    def visit_GeneratorExp(self,node):
        """
        Comprehensions are not allowed in PyRI to reduce complexity
        """
        self.not_allowed(node)

    def visit_DictComp(self,node):
        """
        Comprehensions are not allowed in PyRI to reduce complexity
        """
        self.not_allowed(node)

    def visit_comprehension(self,node):
        """
        Comprehensions are not allowed in PyRI to reduce complexity
        """
        self.not_allowed(node)

    # Statements

    

    def visit_Assign(self,node):
        """
        Check local variables to prevent overwriting assigned names
        """
        if len(node.targets) != 1:
            self.error(node, 'Multiple assign targets are not allowed')

        ret_node = super().visit_Assign(node)

        return self.check_assign_name(node,ret_node)

    def visit_AugAssign(self,node):
        """
        Deny use of AugAssign. Adds complexity, and most industrial languages don't support it anyway
        """
        self.not_allowed(node)
    
    def get_assign_names_tuple(self,t):
        names = []        
        for t1 in t.elts:
            if isinstance(t1,ast.Name):
                names.append(t1.id)
            elif isinstance(t1,(ast.Tuple,ast.List)):
                names.extend(self.get_assign_names_tuple(t1))
        return names


    def check_assign_name(self,node,ret_node):
        
        if isinstance(ret_node,list):
            ret_node = ret_node[0]
        # Add check for variable assignment to prevent overwriting
        # builtins or global variables

        names = []
        if hasattr(node,'targets'):
            t = node.targets[0]
        else:
            t = node.target
        if not (isinstance(t, ast.Tuple)):
            if isinstance(t,ast.Name):
                names.append(t.id)
            elif isinstance(t,(ast.Tuple,ast.List)):
                names.extend(self.get_assign_names_tuple(t))
        else:
            for t1 in t.elts:
                if isinstance(t1,ast.Name):
                    names.append(t1.id)
                elif isinstance(t1,(ast.Tuple,ast.List)):
                    names.extend(self.get_assign_names_tuple(t1))
        
        new_nodes = []

        if (len(names) != 0):
            
            for n in names:
                new_node = ast.Expr(
                    value = ast.Call(func=ast.Name('_check_assign_name_'),
                        args=[ast.Constant(value=n)],
                        keywords=[]
                    )
                )
                copy_locations(new_node, node)
                new_nodes.append(new_node)
        
        new_nodes.append(ret_node)
        
        return new_nodes

        

    def visit_Delete(self, node):
        
        """
        Don't allow deletion of local variables
        """

        if len(node.targets) != 1:
            self.error(node, 'del may only contain one target')
            return super().visit_Delete(node)
        
        t = node.targets[0]
       
        if isinstance(t,ast.Name):
            self.error(node, 'Deleting local variable "{name}" is not allowed'.format(name=t.id))
            return super().visit_Delete(node)

        return super().visit_Delete(node)

        
    def visit_For(self,node):
        """
        Check the local variable names
        """
        ret_node = super().visit_For(node)
        return self.check_assign_name(node,ret_node)

    def visit_Try(self,node):
        """
        Check the assigned names of exceptions
        """
        ret_node = super().visit_Try(node)

        names = []
        for h in ret_node.handlers:
            if h.name is not None:
                names.append(h.name)
        
        new_nodes = []

        if (len(names) != 0):
            
            for n in names:
                new_node = ast.Expr(
                    value = ast.Call(func=ast.Name('_check_assign_name_'),
                        args=[ast.Constant(value=n)],
                        keywords=[]
                    )
                )
                copy_locations(new_node, node)
                new_nodes.append(new_node)
        
        new_nodes.append(ret_node)
        
        return new_nodes

    def visit_With(self,node):

        ret_node = super().visit_With(node)

        if len(ret_node.items) > 1:
            self.error(
                node,
                "With statements may only have one item")

        new_nodes = []

        if isinstance(ret_node.items[0].optional_vars,ast.Name):

            n = ret_node.items[0].optional_vars.id            
            new_node = ast.Expr(
                value = ast.Call(func=ast.Name('_check_assign_name_'),
                    args=[ast.Constant(value=n)],
                    keywords=[]
                )
            )
            copy_locations(new_node, node)
            new_nodes.append(new_node)
        
        new_nodes.append(ret_node)
        return new_nodes

    # Function and class definitions

    def visit_FunctionDef(self,node):        
        """
        Don't allow nested functions
        """

        ret_node = super().visit_FunctionDef(node)

        func_visitor = _NestedFunctionCheck()
        for b in node.body:
            func_visitor.visit(b)

        if len(func_visitor.func_nodes) > 0:
            for f in func_visitor.func_nodes:
                self.error(
                    f,
                    "Nested functions are not allowed")

        return ret_node

    def visit_Lambda(self,node):
        """
        Deny `lambda` statements
        """
        return self.not_allowed(node)

    def visit_Yield(self,node):
        """
        Deny `yield` statements
        """
        return self.not_allowed(node)

    def visit_YieldFrom(self,node):
        """
        Deny `yield from` statements
        """
        return self.not_allowed(node)

    def visit_Global(self,node):
        """
        Deny `global` statements
        """

        return self.not_allowed(node)

    def visit_ClassDef(self,node):
        """
        Deny defining classes
        """

        return self.not_allowed(node)

    def visit_NamedExpr(self,node):
        """
        Deny walrus operator
        """

        return self.not_allowed(node)

    def visit_Module(self,node):
        """
        Prevent all top level nodes except for FunctionDef
        """

        for t in node.body:
            if not isinstance(t,ast.FunctionDef):
                self.error(
                    t,
                    "Only functions may be at top level of modules")
        ret_node = super().visit_Module(node)
        return ret_node

class _NestedFunctionCheck(ast.NodeVisitor):

    def __init__(self):
        self.func_nodes = []

    def visit_FunctionDef(self,node):
        self.func_nodes.append(node)