import ast
from typing import Any


class Visitor(ast.NodeVisitor):
    def __init__(self, sns_topic_name):
        self._sns_topic_name = sns_topic_name
        self.method_name = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """
        Find function definitions, look for the decorators,
        and find our sns topic name in the arguments list
        :param node:
        :return:
        """
        for l in node.decorator_list:
            for a in l.args:
                if a.value == self._sns_topic_name:
                    print(node.name)
                    self.method_name = node.name


def trigger_chalice_method():
    f = open('app.py', 'r')

    v = Visitor('ses_tbxofficial_inbound_email')
    v.visit(ast.parse(f.read()))
    f.close()

    # Call the method
    import app
    method_to_call = getattr(app, v.method_name)
    method_to_call(None, None)
