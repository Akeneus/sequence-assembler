from igraph import Graph

from core import CoreAssembler


class DoubleHelixAssembler(CoreAssembler):

    def __init__(self,
                 path="ressource/frag_a.dat",
                 min_weight=1,
                 subfolder="DoubleHelixAssambler"):
        super().__init__(path, min_weight, subfolder)

    def _build_graph(self, path, min_weight) -> Graph:
        """
        Generates a graph for DoubleHelixAssambler based on the
        specified data file

        :param path: Path to the data file
        :return: A graph object based on the datafile
        """

        frag_file = open(path, 'r')
        lines = frag_file.readlines()
        sequences = [line.strip() for line in lines]
        new_sequences = self \
            ._rebuild_sequences_considering_double_helix(sequences)
        graph = Graph(directed=True)
        graph = self._build_vertices(graph, new_sequences)
        graph = self._build_edges(
            graph,
            new_sequences,
            min_weight
        )

        return graph

    def _rebuild_sequences_considering_double_helix(self, l_sequences: list):
        """
        Assumes that the data are from a double helix and determines from which
        strand the sequences are. Taking this into account, rebuilds the data
        list with potential complementary sequences

        :param l_sequences: original sequences
        :return: new sequences
        """
        l_new_sequences = []
        l_new_sequences.append(l_sequences[0])
        l_copy_sequences = l_sequences.copy()
        for sequence in l_copy_sequences[1::]:
            same = 0
            opp = 0
            for saved_sequence in l_new_sequences:
                same += self._check_both_sequences(
                    saved_sequence,
                    sequence)
                opp += self._check_both_sequences(
                    self._get_complement_sequence(sequence),
                    saved_sequence)

            if(same > opp):
                l_new_sequences.append(sequence)
            else:
                l_new_sequences.append(
                    self._get_complement_sequence(sequence)
                )

        return l_new_sequences

    def _check_both_sequences(self, first: str, second: str) -> int:
        """
        Checks the weight of the two sequences to each other
        and adds them

        :param sequence_one: frist sequence
        :param sequnece_two: second sequence
        :return: the added weights
        """
        weight_one = self._check_sequence(first, second)
        weight_two = self._check_sequence(second, first)

        return weight_one + weight_two

    def _get_complement_sequence(self, sequence: str) -> str:
        """
        Forms the complementary sequence to a given sequence. The complement is
        defined as an inverted version where each base is converted to its
        complement base

        :param sequence: Sequence
        :return: Complementary sequence
        """
        res_sequence = sequence
        res_sequence = res_sequence.replace("A", "t")
        res_sequence = res_sequence.replace("T", "a")
        res_sequence = res_sequence.replace("G", "c")
        res_sequence = res_sequence.replace("C", "g")

        return (res_sequence.upper())[::-1]
