# Safety Evaluation System(SES)
import ast


class SafetyEvaluationSystem:
    def __init__(self, allowed_modules=None, disallowed_nodes=None):
        self.allowed_modules = set(allowed_modules or ['math', 'sys', 'numpy'])
        self.disallowed_nodes = set(disallowed_nodes or [ast.FunctionDef, ast.AsyncFunctionDef])
        self.errors = []
        self.checked_files = set()
        self.safety_score = 100

        self.disallowed_node_score = 5
        self.unsafety_import_score = 10

    def add_allowed_module(self, module_name):
        """Add a module to the allowed list."""
        self.allowed_modules.add(module_name)

    def remove_allowed_module(self, module_name):
        """Remove a module from the allowed list."""
        self.allowed_modules.discard(module_name)

    def add_disallowed_node(self, node_type):
        """Add an AST node type to the disallowed list."""
        self.disallowed_nodes.add(node_type)

    def remove_disallowed_node(self, node_type):
        """Remove an AST node type from the disallowed list."""
        self.disallowed_nodes.discard(node_type)

    def _is_allowed_module(self, module_name):
        """Check if the module name is in the allowed list."""
        return module_name in self.allowed_modules

    def _visit_Import(self, node, filename):
        """Handle import statements."""
        for alias in node.names:
            if not self._is_allowed_module(alias.name):
                self.errors.append(f"Unsafe import detected: {alias.name}")
                self.safety_score -= self.unsafety_import_score  # 每发现一个不安全的导入，减去()分

    def _visit_ImportFrom(self, node, filename):
        """Handle from ... import ... statements."""
        if not self._is_allowed_module(node.module):
            self.errors.append(f"Unsafe import detected: {node.module}")
            self.safety_score -= self.unsafety_import_score  # 同样，不安全的导入减分

    def _check_ast(self, tree, filename):
        """Walk through the abstract syntax tree and check."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self._visit_Import(node, filename)
            elif isinstance(node, ast.ImportFrom):
                self._visit_ImportFrom(node, filename)
            elif type(node) in self.disallowed_nodes:
                self.errors.append(f"Disallowed node found: {type(node).__name__}")
                self.safety_score -= self.disallowed_node_score  # 发现不允许的节点类型，减去5分
            else:
                # Only allow imports and class definitions by default
                pass

    def _check_file(self, filename):
        """Recursively check the safety of a file and its dependencies."""
        if filename in self.checked_files:
            return
        self.checked_files.add(filename)
        with open(filename, 'r') as file:
            source = file.read()
            tree = ast.parse(source)
            self._check_ast(tree, filename)

    def check_file(self, filename):
        """Check the safety of the given file and its dependencies."""
        self._check_file(filename)
        return self.safety_score, self.errors
