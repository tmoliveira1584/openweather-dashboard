"""Rastreabilidade dos requisitos até os testes (P-027) e artefatos de requisitos sem stack
(P-026).

Os IDs são lidos do spec (RF, RN e RNF nas tabelas; CA nas listas de critérios de aceite) e da
constitution (P-001 a P-027). Cada um precisa aparecer no nome ou na docstring de pelo menos
um teste (arquitetura, seção 9.3). No nome, `rf_014` vale como RF-014.
"""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
DOCS = ROOT / "docs"
TESTS = ROOT / "tests"

# Termos de stack que não podem aparecer nos artefatos de requisitos (P-026).
STACK_TERMS = re.compile(
    r"\b(Python|FastAPI|Uvicorn|httpx|Pydantic|Starlette|Leaflet|JavaScript|TypeScript|HTML|"
    r"CSS|SVG|pytest|Playwright|conda|Ruff|CARTO|Node\.js|npm|React|SQL|Docker)\b",
    re.IGNORECASE,
)
REQUIREMENT_ARTIFACTS = ["requisitos.md", "product-brief.md", "constitution.md", "spec.md"]


def spec_ids() -> list[str]:
    spec = (DOCS / "spec.md").read_text(encoding="utf-8")
    table_ids = re.findall(r"^\| ((?:RF|RN|RNF)-\d{3}) \|", spec, re.MULTILINE)
    acceptance = re.findall(r"^\d+\. \*\*(CA-\d{3})\*\*", spec, re.MULTILINE)
    return table_ids + acceptance


def principle_ids() -> list[str]:
    constitution = (DOCS / "constitution.md").read_text(encoding="utf-8")
    return re.findall(r"^- \*\*(P-\d{3})\*\*", constitution, re.MULTILINE)


def cited_ids() -> set[str]:
    """IDs citados no nome ou na docstring das funções de teste de `tests/`."""
    cited: set[str] = set()
    for path in TESTS.rglob("test_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                name = node.name.upper().replace("_", "-")
                text = f"{name} {ast.get_docstring(node) or ''}"
                cited.update(re.findall(r"\b(?:RF|RN|RNF|CA|P)-\d{3}\b", text))
    return cited


def test_p_027_spec_and_constitution_have_the_217_ids():
    """P-027: a leitura dos documentos encontra os 217 IDs rastreáveis, sem repetição: 58 RF,
    59 RN, 29 RNF e 44 CA do spec e os princípios P-001 a P-027 (tasks.md, escopo)."""
    ids = spec_ids() + principle_ids()
    prefixes = ("RF", "RN", "RNF", "CA", "P")
    counts = {prefix: sum(i.startswith(f"{prefix}-") for i in ids) for prefix in prefixes}

    assert counts == {"RF": 58, "RN": 59, "RNF": 29, "CA": 44, "P": 27}
    assert len(ids) == len(set(ids)) == 217


@pytest.mark.parametrize("source", ["spec", "constitution"])
def test_p_027_every_requirement_is_cited_by_a_test(source: str):
    """P-027, seção 9.3: todo RF, RN, RNF e CA do spec e todo princípio da constitution
    aparece no nome ou na docstring de pelo menos um teste."""
    ids = spec_ids() if source == "spec" else principle_ids()

    cited = cited_ids()
    missing = [i for i in ids if i not in cited]

    assert missing == []


@pytest.mark.parametrize("artifact", REQUIREMENT_ARTIFACTS)
def test_p_026_requirement_artifacts_have_no_stack_details(artifact: str):
    """P-026: os artefatos de requisitos não citam linguagem, framework, biblioteca nem
    ferramenta. A stack fica só na arquitetura."""
    text = (DOCS / artifact).read_text(encoding="utf-8")

    assert STACK_TERMS.findall(text) == []
