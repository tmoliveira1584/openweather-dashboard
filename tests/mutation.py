"""Teste de mutação sem dependência nova (plano de testes, fase 4, TS-4.1).

Gera mutantes de um módulo Python, um de cada vez: troca um operador de comparação,
aritmético ou lógico, remove um `not`, altera uma constante ou troca um retorno por `None`.
Para cada mutante, grava o módulo alterado, roda os testes indicados e restaura o arquivo
original. O mutante é "detectado" se algum teste falhar e "sobrevivente" se todos passarem.

Uso:
    python -m tests.mutation app/domain/precipitation.py tests/unit

O arquivo original é sempre restaurado, mesmo com erro ou interrupção.
"""

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

COMPARE_SWAPS = {
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
}
BINOP_SWAPS = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult}
BOOLOP_SWAPS = {ast.And: ast.Or, ast.Or: ast.And}
SYMBOLS = {
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Is: "is",
    ast.IsNot: "is not",
    ast.In: "in",
    ast.NotIn: "not in",
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.And: "and",
    ast.Or: "or",
}


@dataclass
class Mutant:
    index: int
    line: int
    description: str


def _docstrings(tree: ast.Module) -> set[int]:
    """`id` das constantes que são docstrings: alterá-las não muda o comportamento."""
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.FunctionDef | ast.ClassDef) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                ids.add(id(first.value))
    return ids


def _mutated_constant(value):
    """Nova constante, ou `None` se o tipo não é mutado. Números ganham 1; textos esvaziam."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int | float):
        return value + 1
    if isinstance(value, str):
        return "" if value else "X"
    return None


class _Mutator(ast.NodeTransformer):
    """Percorre a árvore numerando os pontos de mutação. Com `target`, aplica só aquele."""

    def __init__(self, docstrings: set[int], target: int | None = None):
        self.docstrings = docstrings
        self.target = target
        self.count = 0
        self.found: list[Mutant] = []

    def _point(self, node: ast.AST, description: str) -> bool:
        """Registra um ponto de mutação e diz se ele é o alvo."""
        index = self.count
        self.count += 1
        self.found.append(Mutant(index, node.lineno, description))
        return index == self.target

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        self.generic_visit(node)
        for i, op in enumerate(node.ops):
            swap = COMPARE_SWAPS.get(type(op))
            if swap and self._point(node, f"`{SYMBOLS[type(op)]}` → `{SYMBOLS[swap]}`"):
                node.ops[i] = swap()
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        swap = BINOP_SWAPS.get(type(node.op))
        if swap and self._point(node, f"`{SYMBOLS[type(node.op)]}` → `{SYMBOLS[swap]}`"):
            node.op = swap()
        return node

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.AST:
        self.generic_visit(node)
        swap = BOOLOP_SWAPS[type(node.op)]
        if self._point(node, f"`{SYMBOLS[type(node.op)]}` → `{SYMBOLS[swap]}`"):
            node.op = swap()
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.op, ast.Not) and self._point(node, "`not x` → `x`"):
            return node.operand
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if id(node) in self.docstrings:
            return node
        new = _mutated_constant(node.value)
        if new is not None and self._point(node, f"constante `{node.value!r}` → `{new!r}`"):
            return ast.copy_location(ast.Constant(new), node)
        return node

    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.AST:
        # Partes literais de f-strings não são mutadas: só as expressões dentro delas.
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                self.visit(value)
        return node

    def visit_Return(self, node: ast.Return) -> ast.AST:
        self.generic_visit(node)
        returns_value = not (isinstance(node.value, ast.Constant) and node.value.value is None)
        if node.value is not None and returns_value and self._point(node, "retorno → `None`"):
            node.value = ast.Constant(None)
        return node


def list_mutants(source: str) -> list[Mutant]:
    tree = ast.parse(source)
    mutator = _Mutator(_docstrings(tree))
    mutator.visit(tree)
    return mutator.found


def mutate(source: str, index: int) -> str:
    tree = ast.parse(source)
    _Mutator(_docstrings(tree), target=index).visit(tree)
    return ast.unparse(ast.fix_missing_locations(tree))


def run_tests(tests: list[str]) -> bool:
    """Roda os testes e diz se todos passaram (o mutante sobreviveu)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *tests],
        check=False,
        capture_output=True,
        stdin=subprocess.DEVNULL,
        timeout=300,
    )
    return result.returncode == 0


def main(module: str, tests: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # o console do Windows não imprime "→"
    path = Path(module)
    original = path.read_bytes()
    source = original.decode("utf-8")
    if not run_tests(tests):
        print("Os testes já falham sem mutação: corrija a suíte antes.")
        return 2

    mutants = list_mutants(source)
    survivors = []
    try:
        for mutant in mutants:
            path.write_text(mutate(source, mutant.index), encoding="utf-8")
            survived = run_tests(tests)
            path.write_bytes(original)
            status = "SOBREVIVEU" if survived else "detectado"
            print(f"#{mutant.index:>3} linha {mutant.line:>3}  {status:<10} {mutant.description}")
            if survived:
                survivors.append(mutant)
    finally:
        path.write_bytes(original)

    detected = len(mutants) - len(survivors)
    score = 100 * detected / len(mutants) if mutants else 100.0
    print(f"\nEscore: {detected} de {len(mutants)} mutantes detectados ({score:.1f}%)")
    for mutant in survivors:
        print(f"  sobrevivente #{mutant.index} (linha {mutant.line}): {mutant.description}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:] or ["tests/unit"]))
