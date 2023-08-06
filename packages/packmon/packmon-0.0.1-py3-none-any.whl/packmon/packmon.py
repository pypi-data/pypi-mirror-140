# encode: utf-8

import argparse
from datetime import datetime, timedelta
import json
import os
import re
import sys
import time
from urllib.request import Request, urlopen


VERSION = "0.0.1"
U_A = f"packmon/{VERSION} (https://framagit.org/Mindiell/packmon/-/blob/develop/bot.md)"
PYPI_URL = "https://pypi.org/pypi/"
CONDITIONS = {
    "==": "equal to",
    ">": "greater than",
    ">=": "greater than or equal to",
    "<": "lesser than",
    "<=": "lesser than or equal to",
    "~=": "unknown",
}
STATUS = {
    "1 - Planning": "planning",
    "2 - Pre-Alpha": "pre-alpha",
    "3 - Alpha": "alpha",
    "4 - Beta": "beta",
    "5 - Production/Stable": "stable",
    "6 - Mature": "mature",
    "7 - Inactive": "inactive",
}


def analyze(requirements):
    components = []
    size = len(requirements)
    for idx, requirement in enumerate(requirements):
        print(f"\r{idx+1}/{size}", end="", file=sys.stderr, flush=True)
        try:
            if len(requirement.strip()) == 0 or requirement[0] == "#":
                continue
            component = {
                "name": "",
                "condition": "",
                "version": None,
                "status": "",
                "license": "Unknown",
                "vulnerabilities": [],
                "last_version": "",
                "last_update": None,
                "last_update_human": "",
            }
            if "=" in requirement or ">" in requirement or "<" in requirement:
                result = re.match(
                    "(?P<name>[^>~=<]+)((?P<condition>[>~=<]+)(?P<version>[^; ]+))?.*$",
                    requirement,
                )
                component["name"] = result.group("name")
                component["condition"] = result.group("condition") or None
                component["version"] = result.group("version") or None
            else:
                component["name"] = requirement

            datas = None
            if component["version"] is not None:
                url = f"{PYPI_URL}{component['name']}/{component['version']}/json"
            else:
                url = f"{PYPI_URL}{component['name']}/json"
            request = Request(url, headers={"User-Agent": U_A})
            result = urlopen(request)
            if result.status == 200:
                datas = json.loads(result.read())
                for classifier in datas["info"]["classifiers"]:
                    if classifier.startswith("Development Status"):
                        component["status"] = classifier.split("::")[-1].strip()
                    if classifier.startswith("License"):
                        component["license"] = classifier.split("::")[-1].strip()
                if component["license"] == "Unknown":
                    component["license"] = datas["info"]["license"]
                component["requires_python"] = datas["info"].get("requires_python", None)
                if len(datas.get("vulnerabilities", [])) > 0:
                    component["vulnerabilities"] = [
                        name
                        for vulnerability in datas["vulnerabilities"]
                        for name in vulnerability["aliases"]
                    ]
                last_version = sorted(
                    [v for v in datas["releases"] if len(datas["releases"][v]) > 0],
                    key=lambda x: datetime.strptime(
                        datas["releases"][x][0]["upload_time"], "%Y-%m-%dT%H:%M:%S"
                    ),
                )[-1]
                component["last_version"] = last_version
                component["last_update"] = datetime.strptime(
                    datas["releases"][last_version][0]["upload_time"],
                    "%Y-%m-%dT%H:%M:%S",
                )
                component["last_update_human"] = datetime.strftime(
                    component["last_update"],
                    "%Y-%m-%d",
                )
            components.append(component)
            time.sleep(0.3)
        except Exception as e:
            print(
                f"Error while trying to find informations on {component['name']}"
                f" with version {component['version']}",
                file=sys.stderr,
            )
            print(e, file=sys.stderr)
            continue
    print()
    return components


def output(components, args):
    # This command is here only to enable ANSI escape sequences for Windows CMD
    os.system("")
    update_limit = datetime.now() - timedelta(days=args.delay)
    if args.no_color:
        NORM = ""
        BOLD = ""
        OK = ""
        WARN = ""
        END_WARN = ""
        DANGER = ""
        END_DANGER = ""
    else:
        NORM = "\033[0m"
        BOLD = "\033[1m"
        OK = "\033[92m"
        WARN = f"{BOLD}\033[33m"
        END_WARN = "\033[0m"
        DANGER = f"{BOLD}\033[31m"
        END_DANGER = "\033[0m"

    for component in components:
        if len(component["name"]) <= 27:
            line = f"{component['name']}" + " " * (28 - len(component["name"]))
        else:
            line = f"{component['name']}\n" + " " * 28
        if component["status"] in STATUS:
            if component["status"][0] in "1237":
                line += f"{DANGER}"
            elif component["status"][0] in "4":
                line += f"{WARN}"
            line += f"{STATUS[component['status']]}"
            if component["status"][0] in "1237":
                line += f"{END_DANGER}"
            elif component["status"][0] in "4":
                line += f"{END_WARN}"
            size = len(STATUS[component["status"]])
        else:
            line += f"{WARN}unknown{END_WARN}"
            size = 7
        line += " " * (10 - size)
        line += f"{component['license']}" + " " * (30 - len(component["license"]))
        if component["version"] is not None:
            if component["version"] != component["last_version"]:
                if (
                    component["version"].split(".")[0]
                    != component["last_version"].split(".")[0]
                ):
                    line += f"{DANGER}{component['version']}{END_DANGER}"
                else:
                    line += f"{WARN}{component['version']}{END_WARN}"
            else:
                line += f"{component['version']}"
            line += " " * (16 - len(component["version"]))
        else:
            line += f"{WARN}unknown{END_WARN}   "
        line += f"{component['last_version']}"
        line += " " * (16 - len(component["last_version"]))
        if component["last_update"] < update_limit:
            line += f"{WARN}{component['last_update_human']}{END_WARN}"
        else:
            line += f"{component['last_update_human']}"
        line += " " * (14 - len(component["last_update_human"]))
        if len(component["vulnerabilities"]) > 0:
            line += f"{DANGER}{len(component['vulnerabilities'])}{END_DANGER}"
        else:
            line += f"{OK}0{NORM}"
        print(line)
        if len(component["vulnerabilities"]) > 0:
            idx_start = 0
            idx_end = 1
            while idx_end <= len(component["vulnerabilities"]):
                while len(
                    ", ".join(component["vulnerabilities"][idx_start:idx_end])
                ) < 70 and idx_end <= len(component["vulnerabilities"]):
                    idx_end += 1
                line = f"{DANGER}{', '.join(component['vulnerabilities'][idx_start:idx_end-1])}{END_DANGER}"
                print(" " * (88 - len(line)) + line)
                idx_start = idx_end - 1


def main():
    parser = argparse.ArgumentParser(description="Analyse requirements FILE(s).")
    # version
    parser.add_argument(
        "--version",
        action="store_const",
        const=True,
        default=False,
        help="output version information and exit",
    )
    # requirement file
    parser.add_argument(
        "FILE",
        nargs="*",
        help="files to analyse; if no file given, read standard input",
    )
    # colorize output
    parser.add_argument(
        "--no-color",
        action="store_const",
        const=True,
        default=False,
        help="output is displayed without ANSI escapes colors",
    )
    # delay (in days)
    parser.add_argument(
        "--delay",
        default=360,
        type=int,
        help=(
            "delay, in days, after which last release is considered obsolete "
            "(default to 360)"
        ),
    )
    args = parser.parse_args()
    if args.version:
        print(f"Version {VERSION}")
    else:
        requirements = []
        if len(args.FILE) == 0:
            line = input()
            try:
                while line != "":
                    requirements.append(line)
                    line = input()
            except EOFError:
                pass
        else:
            for filename in args.FILE:
                with open(filename) as file_handler:
                    requirements.extend(file_handler.read().splitlines())

        output(analyze(requirements), args)
