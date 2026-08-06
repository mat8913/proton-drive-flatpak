#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p "python3.withPackages(ps: [ ps.requests ps.ruamel-yaml ])"

import requests
import sys
from pathlib import Path

from ruamel.yaml import YAML

VERSION_URL = "https://proton.me/download/drive/cli/version.json"
MANIFEST = Path("ch.proton.drive.yml")


def main():
    response = requests.get(VERSION_URL)
    response.raise_for_status()
    data = response.json()

    releases = data["Releases"]
    release = next(x for x in releases if x.get("CategoryName") == "Stable")
    version = release["Version"]
    files = release["Files"]

    print(f"Version {version}")

    x64 = next(x for x in files if x.get("Platform") == "linux/x64")
    arm64 = next(x for x in files if x.get("Platform") == "linux/arm64")

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 9999

    with MANIFEST.open() as f:
        manifest = yaml.load(f)

    for module in manifest["modules"]:
        if module["name"] != "proton-drive-cli":
            continue
        for source in module["sources"]:
            arches = source.get("only-arches")
            if ["x86_64"] == arches:
                source["url"] = x64["Url"]
                source["sha512"] = x64["Sha512CheckSum"]
            elif ["aarch64"] == arches:
                source["url"] = arm64["Url"]
                source["sha512"] = arm64["Sha512CheckSum"]

    with MANIFEST.open("w") as f:
        yaml.dump(manifest, f)


if __name__ == "__main__":
    main()
