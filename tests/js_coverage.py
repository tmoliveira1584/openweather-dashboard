"""Cobertura do JavaScript medida pelo próprio Chrome (plano de testes, fase 1, TS-1.2).

Com `--js-coverage`, cada página dos testes de ponta a ponta liga a cobertura precisa do V8
pelo protocolo de depuração do Chrome (CDP `Profiler.startPreciseCoverage`), sem dependência
nova (ADR-014). No fim de cada teste, os trechos executados de `static/js/` são somados. No fim
da sessão, a cobertura de linhas por arquivo vai para o terminal e para `coverage-js/`.

Uma linha conta quando tem código (não só espaço ou comentário). Ela está coberta quando algum
caractere de código dela foi executado em algum teste. Os arquivos de `static/js/` que nenhum
teste carregou entram no relatório com 0%.
"""

import json
from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError

ROOT = Path(__file__).parent.parent
JS_DIR = ROOT / "static" / "js"
REPORT_DIR = ROOT / "coverage-js"

_executed: dict[str, list[bool]] = {}


def pytest_addoption(parser):
    parser.addoption(
        "--js-coverage",
        action="store_true",
        help="mede a cobertura de static/js/ no Chrome e grava o relatório em coverage-js/",
    )


@pytest.fixture(autouse=True)
def _js_coverage(request):
    """Liga a cobertura do V8 na página do teste, antes de qualquer navegação."""
    if not request.config.getoption("--js-coverage") or "page" not in request.fixturenames:
        yield
        return
    page = request.getfixturevalue("page")
    base_url = request.getfixturevalue("base_url")
    cdp = page.context.new_cdp_session(page)
    cdp.send("Profiler.enable")
    cdp.send("Profiler.startPreciseCoverage", {"callCount": True, "detailed": True})
    yield
    try:
        result = cdp.send("Profiler.takePreciseCoverage")["result"]
    except PlaywrightError:  # página já fechada pelo próprio teste
        return
    for script in result:
        _add_script(script, f"{base_url}/js/")


def _add_script(script: dict, prefix: str) -> None:
    """Soma os trechos executados de um script de `static/js/` (offsets em UTF-16)."""
    url = script["url"].split("?")[0]
    if not url.startswith(prefix):
        return
    relative = url[len(prefix) :]
    source = _read(JS_DIR / relative)
    if source is None:
        return
    size = len(source.encode("utf-16-le")) // 2
    counts = [0] * size
    ranges = [r for function in script["functions"] for r in function["ranges"]]
    # Trechos externos antes dos internos: o mais interno define a contagem de cada caractere.
    ranges.sort(key=lambda r: (r["startOffset"], -r["endOffset"]))
    for r in ranges:
        end = min(r["endOffset"], size)
        counts[r["startOffset"] : end] = [r["count"]] * (end - r["startOffset"])
    executed = _executed.setdefault(relative, [False] * size)
    for i, count in enumerate(counts):
        if count:
            executed[i] = True


def _read(path: Path) -> str | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8", newline="") as file:
        return file.read()


def code_mask(source: str) -> list[bool]:
    """Marca, por caractere, o que é código: fora de comentários e diferente de espaço."""
    mask = [False] * len(source)
    i, n = 0, len(source)
    quote = None
    while i < n:
        ch = source[i]
        if quote:
            mask[i] = True
            if ch == "\\":
                if i + 1 < n:
                    mask[i + 1] = True
                i += 2
                continue
            if ch == quote:
                quote = None
        elif source.startswith("//", i):
            end = source.find("\n", i)
            i = n if end == -1 else end
            continue
        elif source.startswith("/*", i):
            end = source.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        elif ch in "'\"`":
            quote = ch
            mask[i] = True
        elif not ch.isspace():
            mask[i] = True
        i += 1
    return mask


def line_coverage(
    source: str, executed: list[bool] | None
) -> tuple[list[int], list[int], list[int]]:
    """Devolve (linhas com código, linhas sem execução, linhas parciais), a partir de 1.

    Parcial é a linha executada em que algum trecho de código nunca rodou, como o outro lado
    de um `?:`, de um `??` ou de um `if` de uma linha só: é a medida de ramos do V8.
    """
    mask = code_mask(source)
    lines, missing, partial = [], [], []
    char = unit = 0
    for number, text in enumerate(source.splitlines(keepends=True), start=1):
        is_code = is_run = is_skipped = False
        for ch in text:
            if mask[char]:
                is_code = True
                if executed and unit < len(executed) and executed[unit]:
                    is_run = True
                else:
                    is_skipped = True
            char += 1
            unit += 2 if ord(ch) > 0xFFFF else 1
        if is_code:
            lines.append(number)
            if not is_run:
                missing.append(number)
            elif is_skipped:
                partial.append(number)
    return lines, missing, partial


def _ranges(numbers: list[int]) -> str:
    """[3, 4, 5, 9] -> "3-5, 9"."""
    parts, start = [], None
    for i, n in enumerate(numbers):
        if start is None:
            start = n
        if i + 1 == len(numbers) or numbers[i + 1] != n + 1:
            parts.append(str(start) if start == n else f"{start}-{n}")
            start = None
    return ", ".join(parts)


def build_report() -> dict:
    files = {}
    for path in sorted(JS_DIR.rglob("*.js")):
        relative = path.relative_to(JS_DIR).as_posix()
        lines, missing, partial = line_coverage(_read(path), _executed.get(relative))
        files[relative] = {
            "lines": len(lines),
            "covered": len(lines) - len(missing),
            "percent": round(100 * (len(lines) - len(missing)) / len(lines), 1) if lines else 100,
            "missing": _ranges(missing),
            "partial": _ranges(partial),
        }
    total = sum(f["lines"] for f in files.values())
    covered = sum(f["covered"] for f in files.values())
    return {
        "files": files,
        "total": {"lines": total, "covered": covered, "percent": round(100 * covered / total, 1)},
    }


def pytest_terminal_summary(terminalreporter, config):
    if not config.getoption("--js-coverage") or not _executed:
        return
    report = build_report()
    width = max(len(name) for name in report["files"]) + len("static/js/")
    rows = [f"{'Arquivo':<{width}} {'Linhas':>6} {'Cobertas':>8} {'%':>6}  Sem execução"]
    for name, f in report["files"].items():
        path = f"static/js/{name}"
        rows.append(
            f"{path:<{width}} {f['lines']:>6} {f['covered']:>8} {f['percent']:>6}  {f['missing']}"
        )
    t = report["total"]
    rows.append(f"{'TOTAL':<{width}} {t['lines']:>6} {t['covered']:>8} {t['percent']:>6}")
    rows += ["", "Linhas parciais (algum trecho da linha nunca rodou):"]
    rows += [
        f"static/js/{name}: {f['partial']}" for name, f in report["files"].items() if f["partial"]
    ]
    text = "\n".join(rows) + "\n"
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "coverage.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (REPORT_DIR / "report.txt").write_text(text, encoding="utf-8")
    terminalreporter.section("cobertura do JavaScript (Chrome, V8)")
    terminalreporter.write(text)
