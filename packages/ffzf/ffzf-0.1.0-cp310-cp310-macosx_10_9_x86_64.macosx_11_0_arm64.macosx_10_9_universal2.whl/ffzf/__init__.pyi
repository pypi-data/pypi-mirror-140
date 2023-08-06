def closest(target: str, candidates: list[str], algorithm: str = "levenshtein") -> str:
    """
    Find the closest match to the target string in the list of candidates.
    :param target: The target string to find a match for.
    :param candidates: The list of strings to find a match in.
    :param algorithm: The algorithm to use for finding the closest match. Options are:
        - "levenshtein"
        - "jaro"
        - "jarowinkler"
        - "hamming"
    """
    ...

def n_closest(target: str, candidates: list[str], n: int, algorithm: str = "levenshtein") -> list[str]:
    """
    Find the n closest matches to the target string in the list of candidates.
    :param target: The target string to find a match for.
    :param candidates: The list of strings to find a match in.
    :param n: The number of closest matches to return.
    :param algorithm: The algorithm to use for finding the closest match. Options are:
        - "levenshtein"
        - "jaro"
        - "jarowinkler"
        - "hamming"
    """
    ...

