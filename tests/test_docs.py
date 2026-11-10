"""The agent docs must stay true: every export documented, llms files fresh, doc snippets valid."""

from __future__ import annotations

import ast
import builtins
import inspect
import re

import pytest

import aion
from aion import catalog
from aion._env import ROOT

BLOCK = re.compile(r"```python\n(.*?)```", re.S)
DOCS = [ROOT / "CHEATSHEET.md", *sorted((ROOT / "docs").glob("*.md"))]


def _blocks(path):
    return [(path.name, i, src) for i, src in enumerate(BLOCK.findall(path.read_text()))]


ALL_BLOCKS = [b for p in DOCS for b in _blocks(p)]


def test_every_export_has_summary_and_example():
    bad = [e.name for e in catalog.entries() if not e.summary or not e.example]
    assert not bad, f"add a docstring summary + Example: for {bad}"


def test_llms_files_are_fresh():
    api, full = catalog.build_llms(ROOT)
    llms = (ROOT / "llms.txt").read_text()
    assert api.strip() in llms, "llms.txt is stale: run `uv run aion docs --build`"
    assert (ROOT / "llms-full.txt").read_text() == full, "llms-full.txt is stale: run `uv run aion docs --build`"


def test_llms_links_exist():
    for link in re.findall(r"\]\(([^)]+)\)", (ROOT / "llms.txt").read_text()):
        assert (ROOT / link).exists(), link


def test_agents_commands_exist():
    from aion.cli import main

    names = set(main.list_commands(None))
    table = (ROOT / "AGENTS.md").read_text().split("## Commands")[1].split("##")[0]
    rows = [l.split("|")[2] for l in table.splitlines() if l.startswith("| ") and l.count("|") >= 3]
    used = {m for col in rows[1:] for m in re.findall(r"`([a-z]+)[ `]", col)}
    assert len(used) >= 10
    assert used <= names, f"AGENTS.md mentions missing commands: {used - names}"


@pytest.mark.parametrize("name,i,src", ALL_BLOCKS, ids=[f"{n}#{i}" for n, i, _ in ALL_BLOCKS])
def test_doc_snippets_compile_and_bind(name, i, src):
    """Snippets compile, and every call to an aion export uses real parameter names."""
    tree = ast.parse(src)
    reg = aion.registry()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in reg:
            obj = getattr(aion, node.func.id)
            try:
                sig = inspect.signature(obj)
            except (TypeError, ValueError):
                continue
            if any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords):
                continue
            try:
                sig.bind(*[None] * len(node.args), **{k.arg: None for k in node.keywords})
            except TypeError as e:
                pytest.fail(f"{name} block {i}: {node.func.id}(...) does not match {sig}: {e}")


CHEAT = [b for b in ALL_BLOCKS if b[0] == "CHEATSHEET.md"]


@pytest.mark.parametrize("name,i,src", CHEAT, ids=[f"cheat#{i}" for _, i, _ in CHEAT])
def test_cheatsheet_names_exist(name, i, src):
    """Every free name in a cheatsheet block is defined there, a builtin, or exported by aion."""
    tree = ast.parse(src)
    defined = {"T", "s", "cache"}       # conventional: beats table, scene builder, a baked SimCache
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            defined |= {a.arg for a in node.args.args}
            if isinstance(node, ast.FunctionDef):
                defined.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined.add(node.id)
        elif isinstance(node, ast.alias):
            defined.add(node.asname or node.name)
    missing = sorted({n.id for n in ast.walk(tree)
                      if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
                      and n.id not in defined and not hasattr(builtins, n.id) and not hasattr(aion, n.id)})
    assert not missing, f"cheatsheet block {i} uses unknown names {missing}"
