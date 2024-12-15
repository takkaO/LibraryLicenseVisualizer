import json
from pprint import pprint
from pathlib import Path
from collections import defaultdict
import re
import os
from tree_to_mmd import export_to_mermaidjs


def organize_files_by_library(result_json_path: str):
    scan_result = None
    with open(result_json_path, "r") as f:
        scan_result = json.load(f)

    # マッチ条件の正規表現パターン
    patterns = [
        re.compile(
            r".*licen(s|c)e.*", re.IGNORECASE
        ),  # LICENSEまたはLICENCE、大文字小文字問わず、拡張子付きも許容
        re.compile(
            r".*readme.*", re.IGNORECASE
        ),  # README、大文字小文字問わず、拡張子付きも許容
        re.compile(
            r".*copyright.*", re.IGNORECASE
        ),  # COPYRIGHT、大文字小文字問わず、拡張子付きも許容
        re.compile(r".*\.h(pp|p)?$", re.IGNORECASE),  # .h, .hpp, .hp
        re.compile(r".*\.c(pp|p|xx|c)?$", re.IGNORECASE),  # .c, .cc, .cpp, .cp, .cxx
    ]

    libraries = defaultdict(list)
    for item in scan_result["files"]:
        if item["type"] == "directory":
            # ディレクトリはスキップ
            continue

        if not any(pattern.search(item["name"]) for pattern in patterns):
            # 不要ファイルはスキップ
            continue

        try:
            lib_name = Path(item["path"]).parents[-3].name
            libraries[lib_name].append(item)
        except IndexError:
            print(f'Error: {item["path"]}')
            continue

    return libraries


def create_license_tree_by_library(organized_scan_result):
    tree = {}
    for lib_name, files in organized_scan_result.items():
        tree[lib_name] = dict()
        tree[lib_name]["LicenseFiles"] = defaultdict(list)
        tree[lib_name]["ReadmeFiles"] = defaultdict(list)
        tree[lib_name]["OtherFiles"] = defaultdict(list)

        for file_info in files:
            license_group = defaultdict(set)
            if file_info["license_detections"] == []:
                SCORE = 100
                license_group["NoLicense"].add((file_info["path"], SCORE))

            else:
                for license_info in file_info["license_detections"][0]["matches"]:
                    SPDX = license_info["license_expression_spdx"]
                    license_group[SPDX].add((file_info["path"], license_info["score"]))

            for spdx, values in license_group.items():
                for path, score in values:
                    sub_key = "OtherFiles"
                    if re.search(rf".*/{lib_name}/licen(s|c)e.*", path, re.IGNORECASE):
                        if spdx != "NoLicense":
                            sub_key = "LicenseFiles"
                        else:
                            continue
                    elif re.search(rf".*/{lib_name}/copyright.*", path, re.IGNORECASE):
                        if spdx != "NoLicense":
                            sub_key = "LicenseFiles"
                        else:
                            continue
                    elif re.search(rf".*/{lib_name}/readme.*", path, re.IGNORECASE):
                        if spdx != "NoLicense":
                            sub_key = "ReadmeFiles"
                        else:
                            continue
                    elif not re.search(
                        r".*\.(c|cpp|cp|cxx|cc|h|hpp|hp)?$", path, re.IGNORECASE
                    ):
                        continue

                    tree[lib_name][sub_key][spdx].append(
                        {"path": path, "score": score, "modified": False}
                    )
    return tree


def main():
    obj = organize_files_by_library("./scan_result.json")
    tree = create_license_tree_by_library(obj)
    # pprint(tree)
    s = json.dumps(tree)
    with open("license_tree.json", "w") as f:
        f.write(s)
    export_to_mermaidjs(tree)
    # pprint(tree)


if __name__ == "__main__":
    main()
