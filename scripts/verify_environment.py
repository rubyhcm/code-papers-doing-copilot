#!/usr/bin/env python3
"""Verify the local LogAD benchmark environment without making network calls."""

from __future__ import annotations

import importlib.util
import os
import platform
import sys
from pathlib import Path


def module_version(name: str) -> str:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return "not installed"
    module = __import__(name)
    return str(getattr(module, "__version__", "installed"))


def main() -> int:
    checks = [
        ("Python", ".".join(map(str, sys.version_info[:3]))),
        ("Platform", platform.platform()),
        ("PyTorch", module_version("torch")),
        ("Transformers", module_version("transformers")),
        ("Scikit-learn", module_version("sklearn")),
        ("pandas", module_version("pandas")),
        ("numpy", module_version("numpy")),
        ("drain3", module_version("drain3")),
    ]

    print("=== Environment Verification ===")
    all_ok = True
    for name, value in checks:
        missing = value == "not installed"
        all_ok = all_ok and not missing
        print(f"{'PASS' if not missing else 'FAIL'} {name}: {value}")

    if importlib.util.find_spec("torch") is not None:
        torch = __import__("torch")
        print(f"PASS PyTorch CUDA: {torch.cuda.is_available()}")
        print(f"PASS PyTorch devices: {torch.cuda.device_count()}")
        mps_available = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        print(f"PASS PyTorch MPS: {mps_available}")

    print("=== Source repositories ===")
    root = Path(__file__).resolve().parents[1]
    for name in ("LightAD", "LogFormer", "LogRAG"):
        exists = (root / name).is_dir()
        print(f"{'PASS' if exists else 'FAIL'} {name}: {root / name}")
        all_ok = all_ok and exists

    print("=== Virtual environment ===")
    print(f"{'PASS' if sys.prefix != sys.base_prefix else 'INFO'} active venv: {sys.prefix}")

    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
