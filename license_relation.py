import os
import networkx as nx

class AttributeRelationship:
	def __init__(self):
		"""
		NetworkXの有向グラフを初期化
		"""
		self.graph = nx.DiGraph()
	
	def add_relationship(self, parent, child):
		"""
		属性間の包含関係を追加する
		
		:param parent: 親要素の属性
		:param child: 子要素の属性
		"""
		self.graph.add_edge(child, parent)
	
	def to_mermaid(self):
		"""
		グラフをMermaid記法に変換する
		
		:return: Mermaid記法の文字列
		"""
		# Mermaid記法の開始
		mermaid_lines = ["graph TD"]
		
		# 各エッジをMermaid記法に変換
		for parent, child in self.graph.edges():
			mermaid_lines.append(f"    {child}(\"{child}\") --> {parent}(\"{parent}\")")
		
		# 文字列として結合
		return "\n".join(mermaid_lines)
	
	def is_included(self, child, parent):
		"""
		指定された属性が包含関係にあるかを判定する
		
		:param child: 子属性
		:param parent: 親属性
		:return: 包含関係があるかどうかのブール値
		"""
		if not self.graph.has_node(child):
			return False
		if not self.graph.has_node(parent):
			return False
		return nx.has_path(self.graph, parent, child)
	
	def estimate_most_strong_node(self, nodes):
		"""
		与えられたノード群から、最も制限が強いノードを取得する
		
		:param nodes: 調べたいノードのリスト
		:return: 最も制限が強いと推測されるノード
		"""
		spdx = None
		descendants_num = float("inf")
		ancestors_num = float("inf")
		for node in nodes:
			if not self.graph.has_node(node):
				print(node)
				spdx = node
				continue
			descendants = list(nx.descendants(self.graph, node))
			ancestors = list(nx.ancestors(self.graph, node))

			if ancestors_num < len(ancestors):
				continue
			
			if ancestors_num == len(ancestors):
				if descendants_num < len(descendants):
					continue

			ancestors_num = len(ancestors)
			descendants_num = len(descendants)

			spdx = node
		return spdx

def initialize_license_relationship():
	# 属性関係のインスタンスを作成
	rel = AttributeRelationship()
	
	# 関係を追加（X -> Y）
	rel.add_relationship("LicenseRef-scancode-public-domain", "Unlicense")
	rel.add_relationship("LicenseRef-scancode-public-domain", "LicenseRef-scancode-openwall-md5-permissive")
	rel.add_relationship("LicenseRef-scancode-openwall-md5-permissive", "Unlicense")
	rel.add_relationship("Unlicense", "ISC")
	rel.add_relationship("ISC", "LicenseRef-scancode-ugui")
	rel.add_relationship("LicenseRef-scancode-ugui", "ISC")
	rel.add_relationship("MIT", "LicenseRef-scancode-ugui")
	rel.add_relationship("LicenseRef-scancode-ugui", "MIT")
	rel.add_relationship("MIT", "X11")
	rel.add_relationship("X11", "MIT")
	rel.add_relationship("X11", "BSD-2-Clause")
	rel.add_relationship("BSD-3-Clause", "BSD-4-Clause")
	rel.add_relationship("BSD-3-Clause", "Apache-2.0")
	rel.add_relationship("BSD-3-Clause", "MPL-1.1")
	rel.add_relationship("BSD-3-Clause", "LGPL-2.0-or-later")

	rel.add_relationship("BSD-2-Clause", "FTL")
	rel.add_relationship("FTL", "BSD-3-Clause")

	rel.add_relationship("Apache-2.0", "MPL-2.0-no-copyleft-exception")
	rel.add_relationship("Apache-2.0", "LGPL-3.0-or-later")
	rel.add_relationship("Apache-2.0", "MPL-2.0")

	rel.add_relationship("MPL-1.1", "MPL-2.0-no-copyleft-exception")
	rel.add_relationship("MPL-2.0", "LGPL-2.1-or-later")

	rel.add_relationship("LGPL-2.0-or-later", "LGPL-2.1-or-later")
	rel.add_relationship("LGPL-2.0-or-later", "LGPL-2.0-only")
	rel.add_relationship("LGPL-2.1-or-later", "LGPL-3.0-or-later")
	rel.add_relationship("LGPL-2.1-or-later", "LGPL-2.1-only")
	
	rel.add_relationship("LGPL-2.1-only", "GPL-2.0-or-later")
	rel.add_relationship("LGPL-2.0-only", "GPL-2.0-or-later")
	rel.add_relationship("LGPL-3.0-only", "GPL-3.0-or-later")
	rel.add_relationship("LGPL-3.0-or-later", "LGPL-3.0-only")

	rel.add_relationship("GPL-1.0-or-later", "GPL-2.0-or-later")
	rel.add_relationship("GPL-1.0-or-later", "GPL-1.0-only")

	rel.add_relationship("GPL-2.0-or-later", "GPL-2.0-only")
	rel.add_relationship("GPL-2.0-or-later", "GPL-3.0-or-later")

	rel.add_relationship("GPL-3.0-or-later", "GPL-3.0-only")

	rel.add_relationship("GPL-3.0-only", "AGPL-3.0-or-later")
	rel.add_relationship("AGPL-3.0-or-later", "AGPL-3.0-only")

	return rel

def main():
	rel = initialize_license_relationship()

	# Mermaid記法で出力
	mermaid_graph = rel.to_mermaid()
	
	os.makedirs("./output/", exist_ok=True)
	with open(".//output/license_relation.mmd", "w",  encoding='utf-8') as f:
		f.write(mermaid_graph)

	print("MIT ⊂ X11:", rel.is_included('MIT', 'X11'))  # True
	print("X11 ⊂ MIT:", rel.is_included('X11', 'MIT'))  # True
	print("X11 ⊂ BSD-2-Clause:", rel.is_included('X11', 'BSD-2-Clause'))  # True
	print("BSD-2-Clause ⊂ MIT:", rel.is_included('BSD-2-Clause', "MIT"))  # True
	print("LGPL-3.0-only ⊂ Apache-2.0:", rel.is_included('LGPL-3.0-only', 'Apache-2.0'))  # True
	print("MIT ⊂ Apache-2.0:", rel.is_included('MIT', 'Apache-2.0'))  # True

	test_nodes = ["LGPL-2.0-or-later",  "GPL-3.0-or-later", "AGPL-3.0-only", "GPL-2.0-only", "hoge"]
	final_nodes = rel.estimate_most_strong_node(test_nodes)
	print("最終的なノード:", final_nodes)


if __name__ == "__main__":
	main()