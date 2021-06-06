from typing import List
from datetime import date
from igraph import Graph, plot, os
from assemble_data import AssembleData


class CoreAssambler:

    def __init__(self, path="ressource/frag_a.dat", min_weight=1):
        """
        Entry point for the basic sequence assembler it initializes the
        data and starts the assemble process

        :param min_weight: Lower limit for an edge weight. If the
            overlap is smaller, no edge is added
        :param number_of_iterations: Number of exectuions
        """

        self.min_weight = min_weight
        self.path = path

    def run(self, iterations=1):
        """
        Starts the assemble process

        :param number_of_iterations: Number of exectuions
        """

        for i in range(iterations):
            data = self._setup_data(self.path, self.min_weight)
            self._save_graph(data)
            self._assemble(data)

    @staticmethod
    def _setup_data(path: str, min_weight) -> AssembleData:
        """
        Builds the AssembleData object that contains the state
            of the assemble process

        :param path: Path to the data file
        :return: AssembleData object, representing the initial data
        """

        graph = CoreAssambler._build_graph(path, min_weight)
        source_data_path = CoreAssambler._build_path(path)

        return AssembleData(source_data_path, graph, [])

    @staticmethod
    def _build_graph(path, min_weight) -> Graph:
        """
        Generates a diagram based on the specified data file

        :param path: Path to the data file
        :return: A graph object based on the datafile
        """

        frag_file = open(path, 'r')
        lines = frag_file.readlines()
        sequences = [line.strip() for line in lines]
        graph = Graph(directed=True)
        graph = CoreAssambler._build_vertices(graph, sequences)
        graph = CoreAssambler._build_edges(graph, sequences, min_weight)

        return graph

    @staticmethod
    def _build_vertices(graph: Graph, sequences: List[str]) -> Graph:
        """
        Adds all necessary vertices to the graph
        All vertices contain "name" and "label_id" for easy identification

        :param graph: Graph object
        :param sequences: List of sequences based on the input file
        :return: Graph with added Vertices based on sequences
        """

        graph.add_vertices(len(sequences))
        graph.vs["name"] = sequences
        graph.vs["label_id"] = [id for id in range(len(sequences))]
        return graph

    @staticmethod
    def _build_edges(graph: Graph, sequences: List[str], min_weight) -> Graph:
        """
        Adds edges to the graph, based on the specified sequences. It iterates
        over every Sequence in sequences for each Sequence in sequences
        and performes a prefix check

        :param graph: Graph object
        :param sequences: Sequences to be tested for prefix relationship
        :return: Graph with added Edges based on sequences
        """

        l_edges = []
        l_weights = []
        l_copy_sequences = sequences.copy()
        for sequence_to_check in l_copy_sequences:
            l_sequences_to_check = l_copy_sequences.copy()
            l_sequences_to_check.remove(sequence_to_check)
            for sequence_getting_checked in l_sequences_to_check:
                size_of_matching_prefix = CoreAssambler._check_sequence(
                        sequence_to_check,
                        sequence_getting_checked,
                    )
                if(size_of_matching_prefix >= min_weight):
                    new_edge = (
                        l_copy_sequences.index(sequence_to_check),
                        l_copy_sequences.index(sequence_getting_checked)
                    )
                    l_edges.append(new_edge)
                    l_weights.append(size_of_matching_prefix)

        graph.add_edges(l_edges)
        graph.es["weight"] = l_weights
        return graph

    # Boyer-Moore-Algorithmus
    # Knuth-Morris-Pratt-Algorithmus
    # Suffix-Tree
    @staticmethod
    def _check_sequence(first: str, second: str) -> int:
        """
        Verifys if a subsequence of first is a prefix of second.
        If there is a prefix its length is returned

        :param first: the sequence which shall be checked to be a prefix
        :param second: the sequence which has a potential prefix
        :return: the size of the matching prefixstring
        """

        first_length = len(first)
        v = 0
        for start_index in range(first_length):
            tmp_sub_sequence = first[start_index:first_length]
            if(second.startswith(tmp_sub_sequence)):
                return len(tmp_sub_sequence)
        return v

    @staticmethod
    def _assemble(data: AssembleData):
        """
        Starts the sequence assemble and executes it as long as
        there are edges left

        :param data: AssambleData to work on
        """

        count = data.graph.ecount()
        while(count != 0):
            data = CoreAssambler._unify_nodes(data)
            count = data.graph.ecount()
            CoreAssambler._save_graph(data)
        CoreAssambler._save_substrings(data)

    @staticmethod
    def _unify_nodes(data: AssembleData) -> AssembleData:
        """
        Combines the information of two vertices and to redirect or
        delete affected edges

        :param data: AssembleData object
        :return: reduced AssembleData object
        """

        selected_edge = CoreAssambler._select_highest_weighted_edge(data)
        CoreAssambler._rename_merged_vertice(data, selected_edge)
        CoreAssambler._refactor_graph(data, selected_edge)

        return data

    @staticmethod
    def _select_highest_weighted_edge(data: AssembleData):
        """
        Searches all edges for the heighest edge weight and retruns one

        :param data: AssembleData object
        :return: An edge with the current highest weight
        """

        # find highest weight
        current_highest_weight = max(
            (value for value in data.graph.es["weight"]
                if isinstance(value, int))
        )
        # find all edges with the highest weight
        l_heighest_weighted_edges = data.graph.es.select(
            weight=current_highest_weight
        )

        # TODO optimize
        return l_heighest_weighted_edges[0]

    @staticmethod
    def _rename_merged_vertice(data, selected_edge):
        """
        Renames the Vertices which is the Source of the given edge

        :param data: AssembleData object
        :return: AssembleData with renamed edge
        """

        # select the vertice at the source of the selected_edge
        source_vertice = data.graph.vs[selected_edge.source]

        # select the vertice at the target of the selected_edge
        target_vertice = data.graph.vs[selected_edge.target]

        # merges the name of the target_vertie into the source_vertiec,
        # but only the subsequencce which is not equal
        merged_sequence_name = source_vertice["name"] \
            + target_vertice["name"][selected_edge["weight"]:]

        source_vertice["name"] = merged_sequence_name

        data.sequences.append(
            str(selected_edge["weight"]) + "|"
            + merged_sequence_name + " | "
            + source_vertice["name"] + ":"
            + str(source_vertice["label_id"]) + "<-"
            + target_vertice["name"] + ":"
            + str(target_vertice["label_id"])
        )

        return data

    @staticmethod
    def _refactor_graph(data, selected_edge):
        """
        Refactors the affected parth of the graph after unifycations

        :param data: AssembleData object
        :return: Refactored AssembleData
        """

        # select the vertice at the source of the selected_edge
        source_vertice = data.graph.vs[selected_edge.source]

        # select the vertice at the target of the selected_edge
        target_vertice = data.graph.vs[selected_edge.target]

        # select and then delete all edges which have the soure_vertice
        # as source itself, since the Source vertice gets deleted later
        l_edges_to_delete_with_old_source = list(
            data.graph.es.select(_source=source_vertice)
        )
        if(len(l_edges_to_delete_with_old_source) > 0):
            data.graph.delete_edges(l_edges_to_delete_with_old_source)

        # select and then redirect the edges which have the target_vertice as
        # source, since these edges have the the same word ending, and hence
        # the edge only needs redirection
        l_edges_to_redirect = data.graph.es.select(_source=target_vertice)
        for edge in l_edges_to_redirect:
            # ignore edges on it self
            if(source_vertice.index != edge.target):
                data.graph.add_edge(source_vertice.index, edge.target)
                data.graph.es[-1]["weight"] = edge["weight"]
        data.graph.delete_edges(l_edges_to_redirect)
        data.graph.delete_vertices(target_vertice)

        return data

    @staticmethod
    def _save_graph(data: AssembleData, dis_plot=False):
        """
        Saves a raster graphic of the current graph

        :param data: AssembleData object
        :param data: Flag to disable call to pycario
        """

        visual_style = {}
        visual_style["vertex_shape"] = 'circle'
        visual_style["vertex_size"] = 30
        visual_style["vertex_label"] = data.graph.vs["name"]
        visual_style["edge_label"] = data.graph.es["weight"]
        visual_style["layout"] = data.graph.layout("large")
        visual_style["bbox"] = (1000, 1000)
        visual_style["margin"] = 40
        dir_name = data.data_path + "step_" + str(len(data.sequences)) + ".png"

        if not dis_plot:
            plot(data.graph, dir_name, **visual_style)

    def _save_substrings(data: AssembleData):
        """
        Saves all build substrings into a textfile


        :param data: AssembleData object
        """

        file = open(data.data_path + "_sequences.txt", "w")
        for sequence in data.sequences:
            file.write(sequence + "\n")
        file.close()

    # add parameter
    @staticmethod
    def _build_path(path: str, subfolder: str = "core"):
        """
        _build_path generates a path where the results shall be
        saved based on where the datafile is located

        :param path: Location to store the files
        :return: the path to the created directory
        """
        source_data_name = path.split("/")[-1]
        source_data_name = source_data_name.split(".")[0]
        dir_name = "log/"+source_data_name

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        num_folders = len(os.listdir(dir_name))
        dir_name = dir_name + "/" \
            + subfolder + "/run_" \
            + str(num_folders) + "_" \
            + date.today().strftime("%d-%m-%Y") + "/"
        os.makedirs(dir_name)

        return dir_name


ca = CoreAssambler()
ca.run()
