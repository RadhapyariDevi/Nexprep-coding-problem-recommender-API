import numpy as np

def compute_growth_velocity(rating_history):
    if len(rating_history) < 2:
        return 0.0

    times   = np.array([r["ratingUpdateTimeSeconds"] for r in rating_history])
    ratings = np.array([r["newRating"] for r in rating_history])

    # convert to days from first contest
    times = (times - times[0]) / 86400

    slope = np.polyfit(times, ratings, 1)[0]
    return round(float(slope), 4)  # rating points per day

def current_rating(user_info):
    return user_info.get("rating", 1200)  # default 1200 if unrated