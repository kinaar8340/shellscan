"""Minimal YAML subset for recipes/*.yaml when PyYAML is not installed.

Handles nested maps, dash lists, flow [a,b] and {k: v}, comments, ints/floats.
Not a YAML implementation. Software fact of this loader vs the five shipped files.
"""

from __future__ import annotations

from typing import Any


def load_simple_yaml(text: str) -> Any:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        s = raw.split("#", 1)[0].rstrip()
        if not s.strip():
            continue
        indent = len(s) - len(s.lstrip(" "))
        lines.append((indent, s.strip()))
    val, end = _parse(lines, 0, -1)
    if end != len(lines):
        raise ValueError(f"unconsumed YAML at line {end + 1}: {lines[end][1]}")
    return val


def _parse(lines: list[tuple[int, str]], i: int, parent_indent: int) -> tuple[Any, int]:
    if i >= len(lines):
        return None, i
    indent, tok = lines[i]
    if indent <= parent_indent:
        return None, i
    if tok.startswith("- "):
        return _parse_list(lines, i, indent)
    if ":" in tok and not tok.startswith("{"):
        return _parse_map(lines, i, indent)
    return _scalar(tok), i + 1


def _parse_map(
    lines: list[tuple[int, str]], i: int, indent: int
) -> tuple[dict[str, Any], int]:
    out: dict[str, Any] = {}
    while i < len(lines):
        ind, tok = lines[i]
        if ind < indent:
            break
        if ind > indent:
            raise ValueError(f"bad indent at {tok!r}")
        if tok.startswith("- "):
            break
        if ":" not in tok:
            raise ValueError(f"expected key: value, got {tok!r}")
        key, rest = tok.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        i += 1
        if rest:
            out[key] = _scalar(rest)
            continue
        if i < len(lines) and lines[i][0] > indent:
            child, i = _parse(lines, i, indent)
            out[key] = child
        else:
            out[key] = None
    return out, i


def _parse_list(
    lines: list[tuple[int, str]], i: int, indent: int
) -> tuple[list[Any], int]:
    out: list[Any] = []
    while i < len(lines):
        ind, tok = lines[i]
        if ind != indent or not tok.startswith("- "):
            break
        rest = tok[2:].strip()
        i += 1
        if rest:
            out.append(_scalar(rest))
            continue
        child, i = _parse(lines, i, indent)
        out.append(child)
    return out, i


def _split_flow(inner: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in inner:
        if ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return [p for p in parts if p]


def _scalar(s: str) -> Any:
    s = s.strip()
    if not s:
        return ""
    if s[0] == "[" and s[-1] == "]":
        return [_scalar(p) for p in _split_flow(s[1:-1].strip())]
    if s[0] == "{" and s[-1] == "}":
        out: dict[str, Any] = {}
        for part in _split_flow(s[1:-1].strip()):
            k, v = part.split(":", 1)
            out[k.strip()] = _scalar(v)
        return out
    if (s[0] == s[-1]) and s[0] in "'\"" and len(s) >= 2:
        return s[1:-1]
    if s in ("true", "True", "yes"):
        return True
    if s in ("false", "False", "no"):
        return False
    if s in ("null", "None", "~"):
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s
