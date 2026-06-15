import numpy as np
from datetime import datetime, timezone

HALF_LIFE_DAYS = 30

def recency_decay(timestamp):
    now = datetime.now(timezone.utc).timestamp()
    days_ago = (now - timestamp) / 86400
    return np.exp(-0.693 * days_ago / HALF_LIFE_DAYS)

def difficulty_weight(cf_rating):
    if not cf_rating:
        return 1.5  # default for unrated problems
    return cf_rating / 1000  # 1400 → 1.4, 2200 → 2.2

def build_mastery_vector(processed_submissions, quality_weight=0.75):
    topic_scores = {}
    topic_counts = {}
    skipped = 0

    for sub in processed_submissions:
        if not sub["has_tags"]:
            skipped += 1
            continue

        d = difficulty_weight(sub["cf_rating"])
        r = recency_decay(sub["timestamp"])
        score = d * r

        for tag in sub["tags"]:
            topic_scores[tag] = topic_scores.get(tag, 0.0) + score
            topic_counts[tag] = topic_counts.get(tag, 0) + 1

    if skipped > 0:
        print(f"[mastery] skipped {skipped} submissions with no useful tags")

    if not topic_scores:
        return {}

    # average score per topic
    raw = {t: topic_scores[t] / topic_counts[t] for t in topic_scores}

    # volume bonus — log scaled
    max_count = max(topic_counts.values())
    volume = {
        t: np.log1p(topic_counts[t]) / np.log1p(max_count)
        for t in topic_counts
    }

    # blend quality + volume
    blended = {
        t: quality_weight * raw[t] + (1 - quality_weight) * volume[t]
        for t in raw
    }

    # normalize to 0-1
    min_v = min(blended.values())
    max_v = max(blended.values())
    span = max_v - min_v if max_v != min_v else 1.0

    mastery = {t: round((blended[t] - min_v) / span, 4) for t in blended}

    # sort descending for readability
    return dict(sorted(mastery.items(), key=lambda x: x[1], reverse=True))