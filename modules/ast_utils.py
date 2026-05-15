import subprocess
import os
from pycparser import c_parser, c_ast, parse_file

# Simple fake libc definitions to avoid preprocessor errors with standard headers
FAKE_LIBC = """
typedef int size_t;
typedef int FILE;
int printf(const char* format, ...);
int scanf(const char* format, ...);
"""

def get_ast_from_code(code):
    """
    Parses C code into an AST. Handles preprocessing by stripping includes
    and adding a fake libc for common functions.
    """
    parser = c_parser.CParser()
    # Strip includes because pycparser can't find them without full setup
    lines = []
    for line in code.split('\n'):
        if not line.strip().startswith('#include'):
            lines.append(line)
    
    clean_code = FAKE_LIBC + "\n" + "\n".join(lines)
    
    try:
        ast = parser.parse(clean_code, filename='<none>')
        return ast
    except Exception as e:
        print(f"AST Parsing Error: {e}")
        return None

class FeatureVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.features = {
            "functions": 0,
            "loops": 0,
            "conditions": 0,
            "variables": 0
        }

    def visit_FuncDef(self, node):
        self.features["functions"] += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.features["loops"] += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.features["loops"] += 1
        self.generic_visit(node)

    def visit_DoWhile(self, node):
        self.features["loops"] += 1
        self.generic_visit(node)

    def visit_If(self, node):
        self.features["conditions"] += 1
        self.generic_visit(node)
    
    def visit_Decl(self, node):
        if isinstance(node.type, c_ast.TypeDecl):
            self.features["variables"] += 1
        self.generic_visit(node)

class SignatureVisitor(c_ast.NodeVisitor):
    """
    Implements Algorithm 1 (Plagiarism Checker) logic:
    - Pruning noise (output statements, tiny nodes)
    - Weighting nodes
    - Sorting siblings to handle reordering
    """
    def __init__(self):
        self.signature = []
        # Weights as suggested by Algorithm 1 logic
        self.node_weights = {
            'For': 10, 'While': 10, 'DoWhile': 10,
            'If': 8, 'FuncDef': 15, 'Switch': 8,
            'Assignment': 3, 'Decl': 2,
            'Return': 2, 'FuncCall': 5
        }
        # Noise/Tiny nodes to filter out
        self.noise_types = {'Constant', 'ID', 'Pragma', 'EmptyStatement'}

    def is_output_statement(self, node):
        """Step 1.2: Prune output statements (e.g., printf)"""
        if isinstance(node, c_ast.FuncCall):
            if isinstance(node.name, c_ast.ID) and node.name.name == 'printf':
                return True
        return False

    def get_node_weight(self, node):
        return self.node_weights.get(type(node).__name__, 1)

    def visit(self, node):
        """Custom visit to handle sorting and filtering"""
        if node is None: return
        
        node_type = type(node).__name__

        # Decide whether to record this node in the signature
        is_noise = node_type in self.noise_types or self.is_output_statement(node)
        is_significant = self.get_node_weight(node) >= 2
        
        if not is_noise and is_significant:
            self.signature.append(node_type)

        # Step 2.3: Sort sibling nodes to handle code reordering
        # We ALWAYS visit children (unless it's a noise type we want to prune entirely)
        if not is_noise:
            children = []
            for name, child in node.children():
                children.append((type(child).__name__, child))
            
            # Sort siblings to normalize order (Step 2.3)
            children.sort(key=lambda x: x[0])

            for _, child in children:
                self.visit(child)


def extract_features(code):
    ast = get_ast_from_code(code)
    if not ast:
        return {"functions": 0, "loops": 0, "conditions": 0, "variables": 0}
    
    visitor = FeatureVisitor()
    visitor.visit(ast)
    return visitor.features

def extract_signature(code):
    """
    Step 3.1 & 3.2: Parse and Traverse according to Algorithm 1
    """
    ast = get_ast_from_code(code)
    if not ast:
        return ""
    
    visitor = SignatureVisitor()
    visitor.visit(ast)
    return ",".join(visitor.signature)

