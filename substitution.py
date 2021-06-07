import math

from core import CoreAssembler


class SubstitutionAssembler(CoreAssembler):

    def __init__(self,
                 path="ressource/frag_a.dat",
                 min_weight=1,
                 subfolder="SubsitutionAssambler",
                 plot_flag=False):
        super().__init__(path, min_weight, subfolder, plot_flag=plot_flag)

    def _check_sequence(self, first: str, second: str) -> int:
        """
        Verifys if a subsequence of first is a prefix of second
        while considering possible subsitutions. If there is a
        prefix its length is returned

        :param first: the sequence which shall be checked to be a prefix
        :param second: the sequence which has a potential prefix
        :return: the size of the matching prefixstring
        """
        first_len = len(first)
        second_len = len(second)
        v = 0
        max_error_quoat = self._get_max_error_quota(
            max(first_len, second_len))
        for i in range(first_len):
            current_subsequence = first[i:first_len]
            edit_dist = self._get_edit_distanze(
                second,
                current_subsequence,
            )
            if(edit_dist <= max_error_quoat):
                return len(current_subsequence)

        return v

    def _get_max_error_quota(self, stringLen: int) -> int:
        """
        Calculates the max errors, which a sequence is allowed to have,
        since it is allowed to have 1 error in every 10 chars of a sequence

        :param stringLen: the length of the sequence
        :return: the max number of errors
        """

        return math.ceil(stringLen / 10)

    def _get_edit_distanze(self, first, second):
        """
        Calculates the edit distance between two strings (only substitution!)

        :param first:
        :param second:
        :return: the edit distanz between two Sequences
        """
        edit_dist = 0
        relevant_subsequence = first[0:len(second)]
        for i in range(len(relevant_subsequence)):
            if(relevant_subsequence[i] != second[i]):
                edit_dist += 1

        return edit_dist
