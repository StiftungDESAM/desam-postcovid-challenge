import random
from datetime import datetime, timedelta
import json


def calculate_string_distance(s: str, t: str, algorithm: str = 'levenshtein') -> float:
    """
    Calculate the distance between two strings using the specified algorithm.

    Currently, only the 'levenshtein' algorithm is supported, which computes the
    minimum number of single-character edits (insertions, deletions, or substitutions)
    required to change one string into the other.

    Args:
        s (str): The first input string.
        t (str): The second input string.
        algorithm (str, optional): The string distance algorithm to use.
            Supported values: ['levenshtein']. Default is 'levenshtein'.

    Returns:
        float: The computed string distance.

    Raises:
        ValueError: If an unsupported algorithm is specified.
    """
    if algorithm == "levenshtein":
        return float(calculate_levenshtein_distance(s=s, t=t))
    else:
        raise ValueError(f"Invalid algorithm: {algorithm}. Valid algorithms include ['levenshtein'].")


def calculate_levenshtein_distance(s: str, t: str) -> int:
    """
    Calculate the Levenshtein distance between two strings using a memory-efficient approach.
    
    Args:
        s (str): The first string.
        t (str): The second string.

    Returns:
        int: The Levenshtein distance between the two strings.
    """
    # Ensure s is the shorter string to use less memory
    if len(s) > len(t):
        s, t = t, s

    previous_row = list(range(len(t) + 1))
    
    for i, c1 in enumerate(s, 1):
        current_row = [i]
        for j, c2 in enumerate(t, 1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


# TODO: only for testing...
def random_date_iso(start: str, end: str) -> str:
    """
    Generate a random datetime string in ISO format between two date strings (YYYY-MM-DD).

    Args:
        start (str): Start date in 'YYYY-MM-DD' format.
        end (str): End date in 'YYYY-MM-DD' format.

    Returns:
        str: Random date in 'YYYY-MM-DDTHH:MM:SS' format.
    """
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    delta = end_dt - start_dt
    random_seconds = random.randint(0, int(delta.total_seconds()) - 1)
    rand_dt = start_dt + timedelta(seconds=random_seconds)
    return rand_dt.strftime("%Y-%m-%dT%H:%M:%S")


# TODO: only for testing purposes
def generate_random_metadata(assigned_item_id):
    """
    Generate a randomized metadata dictionary for a given item ID.

    The function creates a metadata dictionary with random values for several fields,
    randomly removes some of these fields, and always includes essential fields such as
    'id', 'tag', 'created', and 'lastUpdated'. The 'created' and 'lastUpdated' fields
    are random dates within the range 2025-04-01 to 2025-05-01.

    Args:
        assigned_item_id (Any): The unique identifier to assign to the 'id' field in the metadata.

    Returns:
        dict: A dictionary containing randomized metadata fields, always including
              'id', 'tag', 'created', and 'lastUpdated'.
    """
    random_dates = [random_date_iso("2025-04-01", "2025-05-01") for i in range(2)]
    metadata = {
        "name": f"Feldname fuer Feld {random.randint(1, 500)}",
        "isStakeholder": random.choice([True, False]),
        "isLeaf": random.choice([True, False]),
        "isVerified": random.choice([True, False]),
    }

    # randomly delete some metadata
    keys = list(metadata.keys())
    keys_to_remove = random.sample(keys, random.randint(0, len(keys)))
    for key in keys_to_remove:
        del metadata[key]

    # this metadata is always in the graph
    metadata["id"] = assigned_item_id
    metadata["tag"] = random.randint(1, 500),
    metadata["created"] = min(random_dates),
    metadata["lastUpdated"] = max(random_dates)

    return metadata


# TODO: this function should probably be put into the knowledge app (is put here for a easier merge request)
def get_metadata_from_knowledge_graph(assigned_item_id: int):

    if assigned_item_id is None:
        return {}

    # TODO: query the knowledge graph
    ...

    # we can't query the knowledge graph right now, so create some random test data
    metadata = generate_random_metadata(assigned_item_id)

    return metadata


def generate_random_codebooks(n_cols: int = 10, n_rows: int = 10, n_codebooks: int = 5) -> str:
    """
    Generate a list of random codebook dictionaries and return them as a JSON string.

    Each codebook contains a specified number of columns and rows. Each row consists of
    a list of cell values and an assigned item ID. The function creates multiple codebooks,
    each with unique names and randomly generated content.

    Args:
        n_cols (int, optional): Number of columns in each codebook. Default is 10.
        n_rows (int, optional): Number of rows in each codebook. Default is 10.
        n_codebooks (int, optional): Number of codebooks to generate. Default is 5.

    Returns:
        str: A JSON-formatted string representing a list of codebook dictionaries.
    """
    input_codebooks = [
        {
            "name": f"codebook_{k}",
            "columns": [f"col_{i}" for i in range(n_cols)],
            "rows": [
                {
                    "cells": [f"value_{i}_{j}" for i in range(n_cols)],
                    "assignedItemID": j
                }
                for j in range(n_rows)
            ]
        }
        for k in range(n_codebooks)
    ]

    return json.dumps(input_codebooks)

