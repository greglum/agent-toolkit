#!/usr/bin/env python3
"""Static Blender Python (bpy) portability and safety linter.

Checks AST patterns that break across Blender 3.x/4.x/5.x, localized UIs, or headless runs.
Exit 0: PASS, 1: FAIL, 2: invalid invocation or syntax error.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys

LOCALIZED_NODE_NAMES = {
    "Principled BSDF",
    "Material Output",
    "Image Texture",
    "Mix Shader",
    "Mix RGB",
    "Background",
    "World Output",
    "Bump",
    "Normal Map",
}

RENAMED_BSDF_SOCKETS = {
    "Subsurface": "Subsurface Weight",
    "Specular": "Specular IOR Level",
    "Emission": "Emission Color",
    "Coat": "Coat Weight",
    "Sheen": "Sheen Weight",
    "Transmission": "Transmission Weight",
}

EEVEE_ENUMS = {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}
BIND_FUNCS = {
    "bind",
    "serve",
    "listen",
    "start_server",
    "create_server",
    "TCPServer",
    "ThreadingTCPServer",
    "HTTPServer",
    "run",
}


def str_const(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def attr_chain(node: ast.AST) -> list[str]:
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    parts.reverse()
    return parts


def handler_catches(node: ast.Try, names: set[str]) -> bool:
    for handler in node.handlers:
        if handler.type is None:
            continue
        if isinstance(handler.type, ast.Name) and handler.type.id in names:
            return True
        if isinstance(handler.type, ast.Tuple):
            for elt in handler.type.elts:
                if isinstance(elt, ast.Name) and elt.id in names:
                    return True
    return False


def restores_object_mode(stmts: list[ast.stmt]) -> bool:
    for stmt in stmts:
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Call) and attr_chain(sub.func)[-2:] == ["object", "mode_set"]:
                for kw in sub.keywords:
                    if kw.arg == "mode" and str_const(kw.value) == "OBJECT":
                        return True
    return False


def is_hasattr_fcurves_guard(test: ast.expr) -> bool:
    for sub in ast.walk(test):
        if isinstance(sub, ast.Call):
            chain = attr_chain(sub.func)
            if chain == ["hasattr"] and len(sub.args) >= 2 and str_const(sub.args[1]) == "fcurves":
                return True
    return False


def contains_wildcard_literal(node: ast.AST) -> bool:
    if str_const(node) == "0.0.0.0":
        return True
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return any(contains_wildcard_literal(elt) for elt in node.elts)
    if isinstance(node, ast.Dict):
        return any(v is not None and contains_wildcard_literal(v) for v in node.values)
    return False


def is_channelbag_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    chain = attr_chain(node.func)
    return any("channelbag" in part.lower() for part in chain)


class BpyLinter(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[dict] = []
        self.eevee_guard_depth = 0
        self.fcurves_guard_depth = 0
        self.mode_restore_depth = 0
        self.channelbag_vars: set[str] = set()

    def add(self, rule: str, node: ast.AST, message: str) -> None:
        self.findings.append({
            "rule": rule,
            "severity": "FAIL",
            "line": getattr(node, "lineno", 1),
            "message": message,
        })

    def visit_Try(self, node: ast.Try) -> None:
        small_try = len(node.body) <= 5 and not any(
            isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for s in node.body
        )
        guards_eevee = handler_catches(node, {"TypeError", "ValueError"}) or (
            small_try and handler_catches(node, {"Exception"})
        )
        guards_fcurves = handler_catches(node, {"AttributeError", "ImportError"}) or (
            small_try and handler_catches(node, {"Exception"})
        )
        restores_mode = restores_object_mode(node.finalbody)
        if guards_eevee:
            self.eevee_guard_depth += 1
        if guards_fcurves:
            self.fcurves_guard_depth += 1
        if restores_mode:
            self.mode_restore_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        if restores_mode:
            self.mode_restore_depth -= 1
        for handler in node.handlers:
            self.visit(handler)
        if guards_eevee:
            self.eevee_guard_depth -= 1
        if guards_fcurves:
            self.fcurves_guard_depth -= 1
        for stmt in node.orelse:
            self.visit(stmt)
        for stmt in node.finalbody:
            self.visit(stmt)

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        guarded = is_hasattr_fcurves_guard(node.test)
        if guarded:
            self.fcurves_guard_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        if guarded:
            self.fcurves_guard_depth -= 1
        for stmt in node.orelse:
            self.visit(stmt)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        key = str_const(node.slice)
        chain = attr_chain(node.value)
        if key in LOCALIZED_NODE_NAMES and chain and chain[-1] == "nodes":
            self.add(
                "localized-node-name",
                node,
                f"node lookup nodes[{key!r}] breaks on localized Blender; match by node.type instead",
            )
        if key in RENAMED_BSDF_SOCKETS and chain and chain[-1] == "inputs":
            modern = RENAMED_BSDF_SOCKETS[key]
            self.add(
                "renamed-bsdf-socket",
                node,
                f"direct inputs[{key!r}] fails in Blender 4.0+; use inputs.get({modern!r}) or inputs.get({key!r})",
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if is_channelbag_call(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.channelbag_vars.add(target.id)
        val = str_const(node.value)
        if val in EEVEE_ENUMS and self.eevee_guard_depth == 0:
            for target in node.targets:
                chain = attr_chain(target)
                if chain and chain[-1] == "engine":
                    self.add(
                        "hardcoded-eevee-enum",
                        node,
                        f"unguarded engine = {val!r} breaks between Blender 4.x and 5.x; probe RNA or wrap in try/except",
                    )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "fcurves" and self.fcurves_guard_depth == 0:
            chain = attr_chain(node.value)
            is_channelbag = (
                is_channelbag_call(node.value)
                or any("channelbag" in part.lower() for part in chain)
                or (isinstance(node.value, ast.Name) and node.value.id in self.channelbag_vars)
            )
            if not is_channelbag:
                self.add(
                    "deprecated-action-fcurves",
                    node,
                    "direct .fcurves access fails in Blender 5.0+ slotted actions; use action_get_channelbag_for_slot with fallback",
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        chain = attr_chain(node.func)
        if chain[-2:] == ["nodes", "get"] and node.args:
            key = str_const(node.args[0])
            if key in LOCALIZED_NODE_NAMES:
                self.add(
                    "localized-node-name",
                    node,
                    f"node lookup nodes.get({key!r}) breaks on localized Blender; match by node.type instead",
                )
        if chain[-2:] == ["object", "mode_set"] and self.mode_restore_depth == 0:
            mode_arg = None
            for kw in node.keywords:
                if kw.arg == "mode":
                    mode_arg = str_const(kw.value)
            if mode_arg != "OBJECT":
                self.add(
                    "unguarded-mode-set",
                    node,
                    "bpy.ops.object.mode_set without try/finally restoring OBJECT mode can leave the scene stuck",
                )
        is_bind_call = bool(chain and chain[-1] in BIND_FUNCS)
        host_kw_wildcard = any(
            kw.arg in {"host", "address", "bind_address"} and contains_wildcard_literal(kw.value)
            for kw in node.keywords
        )
        if host_kw_wildcard or (
            is_bind_call and any(contains_wildcard_literal(arg) for arg in list(node.args) + [kw.value for kw in node.keywords])
        ):
            self.add(
                "wildcard-bind",
                node,
                "binding an unauthenticated Blender socket to 0.0.0.0 exposes arbitrary Python execution on the network",
            )
        self.generic_visit(node)


def lint_source(source: str) -> dict:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"status": "ERROR", "error": f"Python syntax error at line {exc.lineno}: {exc.msg}", "findings": []}
    linter = BpyLinter()
    linter.visit(tree)
    status = "FAIL" if linter.findings else "PASS"
    return {"status": status, "findings": linter.findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="Path to Blender Python (.py) script")
    args = parser.parse_args(argv)
    try:
        target = args.script.resolve(strict=True)
        if not target.is_file():
            raise ValueError(f"target is not a file: {target}")
        source = target.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 2
    report = lint_source(source)
    report["file"] = str(target)
    print(json.dumps(report, indent=2))
    return {"PASS": 0, "FAIL": 1, "ERROR": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
