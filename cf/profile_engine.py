# profile_engine.py  ← new file, paste run() here
from fetcher import get_user_info, get_submissions, get_rating_history
from cache import get_or_fetch
from processor import process_submissions
from mastery import build_mastery_vector
from velocity import compute_growth_velocity, current_rating

def run(handle):
    print(f"\n=== Codeforces profile: {handle} ===\n")
    user_info      = get_or_fetch(handle, "info",    lambda: get_user_info(handle))
    raw_subs       = get_or_fetch(handle, "subs",    lambda: get_submissions(handle, count=500))
    rating_history = get_or_fetch(handle, "ratings", lambda: get_rating_history(handle))

    processed_subs, solved_set = process_submissions(raw_subs)
    mastery  = build_mastery_vector(processed_subs)
    velocity = compute_growth_velocity(rating_history)

    return {
        "handle":          handle,
        "rating":          current_rating(user_info),
        "solved_set":      list(solved_set),
        "mastery_vector":  mastery,
        "growth_velocity": velocity
    }