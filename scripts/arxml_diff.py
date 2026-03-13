"""
arxml_diff.py — ARXML change detection utility

Compares two ARXML files and outputs a structured diff suitable for
piping into the config_agent review workflow.

Usage:
    python arxml_diff.py baseline.arxml modified.arxml [--module COM]
    python arxml_diff.py baseline.arxml modified.arxml --post http://localhost:8001/review
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from typing import Optional


AUTOSAR_NS = {"ar": "http://autosar.org/schema/r4.0"}


def parse_arxml(path: str) -> dict:
    """Parse ARXML file into a flat dict of {path: element_text}."""
    tree = ET.parse(path)
    root = tree.getroot()
    elements = {}

    def walk(node, path=""):
        tag = node.tag.split("}")[-1] if "}" in node.tag else node.tag
        current_path = f"{path}/{tag}"
        name = node.get("name") or node.get("NAME")
        if name:
            current_path = f"{current_path}[{name}]"
        text = (node.text or "").strip()
        if text:
            elements[current_path] = text
        for child in node:
            walk(child, current_path)

    walk(root)
    return elements


def diff_arxml(baseline_path: str, modified_path: str,
               module: Optional[str] = None) -> dict:
    """
    Returns a structured diff between two ARXML files.
    Optionally filters to a specific AUTOSAR module path fragment.
    """
    baseline = parse_arxml(baseline_path)
    modified = parse_arxml(modified_path)

    added   = {k: v for k, v in modified.items() if k not in baseline}
    removed = {k: v for k, v in baseline.items() if k not in modified}
    changed = {
        k: {"before": baseline[k], "after": modified[k]}
        for k in baseline
        if k in modified and baseline[k] != modified[k]
    }

    if module:
        added   = {k: v for k, v in added.items()   if module.upper() in k.upper()}
        removed = {k: v for k, v in removed.items() if module.upper() in k.upper()}
        changed = {k: v for k, v in changed.items() if module.upper() in k.upper()}

    return {
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
        },
        "added":   added,
        "removed": removed,
        "changed": changed,
    }


def main():
    parser = argparse.ArgumentParser(description="ARXML diff utility")
    parser.add_argument("baseline", help="Baseline ARXML file")
    parser.add_argument("modified", help="Modified ARXML file")
    parser.add_argument("--module", help="Filter to module (e.g. COM, DCM, OS)")
    parser.add_argument("--post", help="POST diff to agent endpoint URL")
    args = parser.parse_args()

    result = diff_arxml(args.baseline, args.modified, args.module)
    diff_json = json.dumps(result, indent=2)

    if args.post:
        import urllib.request
        payload = json.dumps({
            "arxml_diff": diff_json,
            "module": args.module or "unknown",
            "requirement_refs": [],
        }).encode()
        req = urllib.request.Request(
            args.post,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            print(resp.read().decode())
    else:
        print(diff_json)


if __name__ == "__main__":
    main()
