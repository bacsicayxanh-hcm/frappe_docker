from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Literal

Repo = Literal["frappe", "erpnext"]
MajorVersion = Literal["12", "13", "14", "15", "develop"]
FrappeRepo = "https://github.com/bacsicayxanh-hcm/frappe"
ErpnextRepo = "https://github.com/bacsicayxanh-hcm/erpnext"
Owner = "bacsicayxanh-hcm"

def get_latest_tag(repo: Repo, version: MajorVersion) -> str:
    if version == "develop":
        return "develop"
    regex = rf"version-{version}"
    refs = subprocess.check_output(
        (
            "git",
            "-c",
            "versionsort.suffix=-",
            "ls-remote",
            "--refs",
            "--heads",
            "--sort=v:refname",
            f"https://github.com/{Owner}/{repo}",
            str(regex),
        ),
        encoding="UTF-8",
    ).split()


    if not refs:
        raise RuntimeError(f'No hashs found for version "{regex}"')
    ref = refs[-1]
    matches: list[str] = re.findall(regex, ref)
    if not matches:
        raise RuntimeError(f'Can\'t parse tag from ref "{ref}"')
    return refs[-2][:10]


def update_env(file_name: str, frappe_tag: str, erpnext_tag: str | None = None):
    text = f"\nFRAPPE_VERSION={frappe_tag}"
    if erpnext_tag:
        text += f"\nERPNEXT_VERSION={erpnext_tag}"

    with open(file_name, "a") as f:
        f.write(text)


def _print_resp(frappe_tag: str, erpnext_tag: str | None = None):
    print(json.dumps({"frappe": frappe_tag, "erpnext": erpnext_tag}))


def main(_args: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", choices=["12", "13", "14", "15", "develop"], required=True
    )
    args = parser.parse_args(_args)

    frappe_tag = get_latest_tag("frappe", args.version)
    erpnext_tag = get_latest_tag("erpnext", args.version)

    file_name = os.getenv("GITHUB_ENV")
    if file_name:
        update_env(file_name, frappe_tag, erpnext_tag)
    _print_resp(frappe_tag, erpnext_tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
