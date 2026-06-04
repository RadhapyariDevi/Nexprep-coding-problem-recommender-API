import numpy as np
from typing import List, Dict

#all leetcode topic tags
ALL_TOPICS = [
    "array",
    "string",
    "hash-table",
    "dynamic-programming",
    "math",
    "sorting",
    "greedy",
    "depth-first-search",
    "breadth-first-search",
    "tree",
    "binary-search",
    "two-pointers",
    "binary-tree",
    "graph",
    "sliding-window",
    "backtracking",
    "stack",
    "heap-priority-queue",
    "union-find",
    "trie",
    "linked-list",
    "recursion",
    "divide-and-conquer",
    "matrix",
    "bit-manipulation",
    "prefix-sum",
    "monotonic-stack",
    "topological-sort",
    "segment-tree",
    "queue",
    "design",
    "binary-indexed-tree",
    "monotonic-queue",
    "shortest-path",
    "database",
    "number-theory",
    "combinatorics",
    "interactive",
    "randomized",
    "string-matching",
    "minimum-spanning-tree",
    "strongly-connected-component",
    "merge-sort",
    "game-theory"
]


TOPIC_INDEX = {t:i for i,t in enumerate(ALL_TOPICS)}

DIFFICULTY_MAP = {
    "Easy": 0.2,
    "Medium": 0.6,
    "Hard": 1.0
}

def get_tag_slug(tag) -> str:
    if isinstance(tag, dict):
        return tag.get("slug", tag.get("tagSlug", "")).lower()
    return str(tag).lower()


def vectorize_problem(problem: dict) -> np.ndarray:
    """
    Converts a problem into a feature vector
    [topic_1, topic_2 ..., difficulty , acceptance]
    """
    vec = np.zeros(len(ALL_TOPICS)+2)

    #one hot encoding for topics
    for tag in problem.get("topicTags", []):
        slug = get_tag_slug(tag)  
        idx = TOPIC_INDEX.get(slug)
        if idx is not None:
            vec[idx] = 1.0
    
    # Difficulty
    vec[-2] = DIFFICULTY_MAP.get(problem.get("difficulty", "Medium"), 0.6)

    # Inverse acceptance (harder to solve = higher score)
    ac_rate = problem.get("acRate", 50.0) / 100.0
    vec[-1] = 1.0 - ac_rate  # 0.85 for 15% AC problem

    return vec



# vectorize user's weakness

def vectorize_user_weakness(mastery_vector: dict, target_difficulty: str) -> np.ndarray:
    """
    Builds the 'ideal problem' vector FROM the user's weak spots.
    Topics with LOW mastery get HIGH weight here — this is the gap vector.
    """
    vec = np.zeros(len(ALL_TOPICS)+2)

    for topic, mastery_score in mastery_vector.items():
        idx = TOPIC_INDEX.get(topic)
        if idx is not None:
            # flip: low mastery → high desired weight
            vec[idx] = 1.0 - mastery_score

    vec[-2] = DIFFICULTY_MAP.get(target_difficulty, 0.6)
    vec[-1] = 0.5  # neutral on acceptance

    return vec


#COSINE SIMILARITY between problem vector and user weakness vector
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


