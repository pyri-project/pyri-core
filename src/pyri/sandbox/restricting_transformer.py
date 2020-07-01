from RestrictedPython.transformer import RestrictingNodeTransformer, ALLOWED_FUNC_NAMES
import ast

class PyriRestrictingNodeTransformer(RestrictingNodeTransformer):
    def __init__(self, errors=None, warnings=None, used_names=None):
        super().__init__(errors,warnings,used_names)

        self.print_info.printed_used=True
        self.print_info.print_used=True
        
        self.special_functions = ["__begin_blockly_statement","__end_blockly_statement"]

    def check_name(self, node, name, allow_magic_methods=False):
        super().check_name(node,name,allow_magic_methods)
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

    def visit_MatMult(self,node):
        """
        MatMult is denied in RestrictedPython. Allow in PyRI
        """
        return self.node_contents_visit(node)

    def visit_Call(self,node):
        """
        Modify Call to allow for calling special functions
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
            return self.node_contents_visit(node)

        # Temporarily change name so name checks are passed
        old_func_id = node.func.id
        node.func.id = "special_placeholder"
        ret_node = self.node_contents_visit(node)
        ret_node.func.id = old_func_id

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
        ret_node = super().visit_Assign(node)
        
        return ret_node
