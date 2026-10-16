"""Compare KiCad's exported netlist with intended pin-to-net assignments."""

from __future__ import annotations

import importlib.util
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gate_generator", ROOT / "generate_schematic.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def parse(text: str):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+', text))

    def item(token: str):
        if token == "(":
            result = []
            while True:
                next_token = next(tokens)
                if next_token == ")":
                    return result
                result.append(item(next_token))
        return token.strip('"')

    return item(next(tokens))


def child(node: list, key: str) -> list:
    return next(part for part in node if isinstance(part, list) and part and part[0] == key)


def main() -> None:
    tree = parse((ROOT / "turnstile-gate.net").read_text())
    actual: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for net in child(tree, "nets")[1:]:
        name = child(net, "name")[1].removeprefix("/")
        for node in net:
            if isinstance(node, list) and node and node[0] == "node":
                actual[name].add((child(node, "ref")[1], child(node, "pin")[1]))

    expected: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for ref, _symbol, _value, _x, _y, nets in module.components:
        for pin, net in nets.items():
            expected[net].add((ref, pin))

    if actual != expected:
        for net in sorted(set(actual) | set(expected)):
            if actual[net] != expected[net]:
                print(net, "expected", sorted(expected[net]), "actual", sorted(actual[net]))
        raise SystemExit(1)
    print(f"Netlist OK: {len(module.components)} komponen, {len(actual)} net, seluruh pin sesuai.")


if __name__ == "__main__":
    main()
