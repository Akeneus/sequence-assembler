from dataclasses import dataclass
from typing import List
from igraph import Graph

@dataclass
class AssembleData:
    """Class for holding information necessary for the squence_assembler"""
    data_name: str
    graph: Graph
    sequences: List[str]