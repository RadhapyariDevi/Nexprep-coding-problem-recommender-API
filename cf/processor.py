CF_TO_UNIFIED = {
    "dp":                       "dp",
    "dynamic programming":      "dp",
    "graphs":                   "graphs",
    "dfs and similar":          "graphs",
    "shortest paths":           "graphs",
    "flows":                    "graphs",
    "trees":                    "trees",
    "greedy":                   "greedy",
    "binary search":            "binary_search",
    "divide and conquer":       "binary_search",
    "math":                     "math",
    "number theory":            "math",
    "combinatorics":            "math",
    "probabilities":            "math",
    "strings":                  "strings",
    "string suffix structures": "strings",
    "two pointers":             "two_pointers",
    "data structures":          "data_structures",
    "sortings":                 "arrays",
    "backtracking":             "backtracking",
    "bitmasks":                 "bit_manipulation",
    "recursion":                "recursion",
    "geometry":                 "geometry",
    "heaps":                    "heaps",
}

BLOCKLIST = {
    "implementation",
    "*special problem",
    "brute force",
    "constructive algorithms",
    "interactive",
    "2-sat",
    "fft",
    "meet-in-the-middle",
    "expression parsing",
    "games",
}

def normalize_tags(raw_tags):
    result = []
    for tag in raw_tags:
        if tag in BLOCKLIST:
            continue
        unified = CF_TO_UNIFIED.get(tag.lower())
        if unified:
            result.append(unified)
    return list(set(result))  # deduplicate

def process_submissions(raw_submissions):
    accepted = []
    solved_set = set()

    for sub in raw_submissions:
        if sub.get("verdict") != "OK":
            continue

        problem = sub["problem"]
        problem_id = f"{problem.get('contestId', 'gym')}_{problem.get('index', '')}"

        # deduplicate — keep only first accepted per problem
        if problem_id in solved_set:
            continue
        solved_set.add(problem_id)

        tags = normalize_tags(problem.get("tags", []))
        rating = problem.get("rating")  # can be None if unrated

        accepted.append({
            "problem_id":  problem_id,
            "title":       problem.get("name", ""),
            "tags":        tags,
            "cf_rating":   rating,
            "timestamp":   sub["creationTimeSeconds"],
            "has_tags":    len(tags) > 0
        })

    return accepted, solved_set