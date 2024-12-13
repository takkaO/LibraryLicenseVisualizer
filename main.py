import json
from pprint import pprint
from pathlib import Path
from collections import defaultdict
import re
import os
from license_relation import initialize_license_relationship

def organize_files_by_library(result_json_path: str):
	scan_result = None
	with open(result_json_path, "r") as f:
		scan_result = json.load(f)

	# マッチ条件の正規表現パターン
	patterns = [
		re.compile(r".*licen(s|c)e.*", re.IGNORECASE),  # LICENSEまたはLICENCE、大文字小文字問わず、拡張子付きも許容
		re.compile(r".*readme.*", re.IGNORECASE),  # README、大文字小文字問わず、拡張子付きも許容
		re.compile(r".*copyright.*", re.IGNORECASE),  # COPYRIGHT、大文字小文字問わず、拡張子付きも許容
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
			exit()

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
				license_group["NoLicense"].add(
					(file_info["path"], SCORE)
				)
			
			else:
				for license_info in file_info["license_detections"][0]["matches"]:
					SPDX = license_info["license_expression_spdx"]
					license_group[SPDX].add(
						(
							file_info["path"],
							license_info["score"]
						)
					)

			for spdx, values in license_group.items():
				for path, score in values:
					sub_key = "OtherFiles"
					if re.search(fr".*/{lib_name}/licen(s|c)e.*", path, re.IGNORECASE):
						if spdx != "NoLicense":
							sub_key = "LicenseFiles"
						else:
							continue
					elif re.search(fr".*/{lib_name}/copyright.*", path, re.IGNORECASE):
						if spdx != "NoLicense":
							sub_key = "LicenseFiles"
						else:
							continue
					elif re.search(fr".*/{lib_name}/readme.*", path, re.IGNORECASE):
						if spdx != "NoLicense":
							sub_key = "ReadmeFiles"
						else:
							continue
					elif not re.search(r".*\.(c|cpp|cp|cxx|cc|h|hpp|hp)?$", path, re.IGNORECASE):
						continue

					tree[lib_name][sub_key][spdx].append({
						"path": path,
						"score": score
					})
	return tree

def get_included_license_list(category):
	l = set()
	for _, license_info in category.items():
		for key in license_info.keys():
			if not key == "NoLicense":
				l.add(key)
	return l

def transform_to_node_name(name):
	return re.sub(r"[-. ]", "_", name)

def create_project_table(lib_name :str, project_license, evidence = {}):
	node_name = transform_to_node_name(lib_name)

	color = "limegreen"
	if project_license == "Unknown":
		color = "gray"

	txt = f'''
{node_name}[
	<table style="background-color:white; color:#222222;">
		<thead>
			<tr style="background-color: blueviolet; color:white">
				<th colspan="4">{lib_name}</th>
			</tr>
			<tr style="background-color: {color};">
				<th colspan="4">{project_license}</th>
			</tr>
		</thead>
		<tbody style="">
	'''

	for spdx, items in evidence.items():
		for item in items:
			txt += '\t\t\t<tr style="background-color: whitesmoke;">\n'

			icon = "✅"
			if not item["score"] == 100:
				icon = "⚠️"

			txt += f'''<td nowrap style="text-align:center;">{icon}</td>
				<td nowrap style="text-align:left;">{spdx}</td>
				<td nowrap style="text-align:left; color: blue; font-size: x-small; vertical-align: bottom; padding-left:2em; padding-right:0.5em;">{item["path"]}</td>
				<td nowrap style="text-align:right; color: blue; font-size: x-small; vertical-align: bottom; padding-left:2em; padding-right:0.5em;">{item["score"]}%</td>
			</tr>
			'''

	txt += f'''</tbody>
	</table>
]
{node_name}@{{shape: text}}
	'''

	return txt

def create_license_group_table(lib_name, file_license_tree, project_license = "Unknown", hide_NoLicense = True):
	txt = ""
	rel = initialize_license_relationship()
	parent_node_name = transform_to_node_name(lib_name)

	if len(file_license_tree.keys()) < 2 or project_license == "Unknown":
		hide_NoLicense = False

	for spdx, items in file_license_tree.items():
		if hide_NoLicense is True and spdx == "NoLicense":
			continue

		color = "skyblue"
		if not rel.is_included(spdx, project_license):
			if spdx == "NoLicense":
				color = "darkgray"
			else:
				color = "tomato"

		node_name = transform_to_node_name(f"{parent_node_name}_{spdx}")

		txt += f'''
		{node_name}[
			<table style="background-color:white; color:#222222;">
				<thead style="background-color: {color};">
					<tr>
						<th colspan="3">{spdx}</th>
					</tr>
				</thead>
				<tbody style="">
		'''

		for file_info in items:
			icon = "✅"
			if not file_info["score"] == 100:
				icon = "⚠️"
			txt += f'''<tr style="background-color: whitesmoke;">
            <td style="text-align:center;">{icon}</td>
            <td style="text-align:left;">{file_info["path"]}</td>
            <td style="text-align:right; color: blue; font-size: x-small; vertical-align: bottom; padding-left:2em; padding-right:0.5em;">{file_info["score"]}%</td>
			</tr>
			'''

		txt += f'''</tbody>
			</table>
		]
		{node_name}@{{shape: text}}
		{parent_node_name} --> {node_name}
		'''

	return txt
			

def export_to_mermaidjs(license_tree):
	txt = "---\n"
	txt += "config:\n"
	txt += "    maxTextSize: 90000\n"
	txt += "---\n"
	txt += "graph LR\n"
	rel = initialize_license_relationship()

	for lib_name, category in license_tree.items():
		project_license = "Unknown"

		if len(category["LicenseFiles"].keys()) != 0:
			# ライセンスファイルが存在
			project_license = rel.estimate_most_strong_node(category["LicenseFiles"].keys())
			txt += create_project_table(lib_name, project_license, category["LicenseFiles"])
		elif len(category["ReadmeFiles"].keys()) != 0:
			# ライセンスファイルなし＆Readmeが存在
			project_license = rel.estimate_most_strong_node(category["ReadmeFiles"].keys())
			txt += create_project_table(lib_name, project_license, category["ReadmeFiles"])
		else:
			# ライセンスファイルなし＆Readmeもなし
			if "NoLicense" not in category["OtherFiles"].keys():
				# 全てのファイルにライセンス情報が記載されている場合
				project_license = rel.estimate_most_strong_node(get_included_license_list(category))
			else:
				# ライセンス情報に不明なものが含まれている場合
				project_license = "Unknown"
			txt += create_project_table(lib_name, project_license)
		
		txt += create_license_group_table(lib_name, category["OtherFiles"], project_license, hide_NoLicense=True)
	
	os.makedirs("./output/", exist_ok=True)
	with open("./output/license_list.mmd", "w",  encoding='utf-8') as f:
		f.write(txt)

	return

def main():
	obj = organize_files_by_library("./scan_result.json")
	tree = create_license_tree_by_library(obj)
	#pprint(tree)

	export_to_mermaidjs(tree)
	#pprint(tree)


if __name__ == "__main__":
	main()