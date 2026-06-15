
# recommendation_pipeline.py
import json
import os
from cf.database import problems_collection
from cf.profile_engine import run as run_profile_engine
import random


PREREQUISITES = {
    "recursion": ["arrays", "math"],
    "trees": ["recursion", "data_structures"],
    "graphs": ["trees"],
    "dp": ["recursion", "math"]
}

def are_prereqs_satisfied(target_tag, user_mastery):
    """Prevents recommending advanced topics if structural foundations are missing."""
    if target_tag not in PREREQUISITES:
        return True
    for parent in PREREQUISITES[target_tag]:
        if user_mastery.get(parent, 0.0) < 0.40:  # 0.40 Competence threshold
            return False
    return True

def map_mastery_level(score):
    if score < 0.40: return "beginner"
    elif score < 0.75: return "intermediate"
    return "advanced"


def generate_production_payload(handle):
    print(f"\n[engine] Extracting live skill matrix for: {handle}...")
    profile = run_profile_engine(handle)
    
    current_rating = profile["rating"]
    solved_set = list(profile["solved_set"])
    mastery = profile["mastery_vector"]
    velocity = profile["growth_velocity"]
    
    # Establish absolute competitive boundaries based on user ranking tier
    # Locks out trivial problems while setting clear upper ceilings
    min_r = max(800, current_rating - 200)
    max_r = current_rating + (300 if velocity >= 1.0 else 200)
    
    print(f"[database] Fetching candidates from MongoDB Atlas index range: [{min_r} - {max_r}]...")
    
    query = {
        "cf_rating": {"$gte": min_r, "$lte": max_r},
        "_id": {"$nin": solved_set}
    }
    query_candidates = list(problems_collection.find(query))
    
    tag_weakness = {tag: 1.0 - score for tag, score in mastery.items()}
    scored_candidates = []
    
    for prob in query_candidates:
        prob_tags = prob["tags"]
        if not prob_tags: 
            continue
            
        # Guardrail A: Check Prerequisites
        blocked_by_prereq = False
        has_untouched_topic = False
        for t in prob_tags:
            if not are_prereqs_satisfied(t, mastery):
                blocked_by_prereq = True
                break
            if mastery.get(t, 0.0) <= 0.1:
                has_untouched_topic = True
                
        if blocked_by_prereq:
            continue
            
        # 1. Base Fitness Score from Topic Deficits
        fit_score = sum(tag_weakness.get(t, 1.0) for t in prob_tags)
        
        # 2. Rigorous Distance Matrix Scoring
        prob_rating = prob["cf_rating"]
        rating_delta = prob_rating - current_rating
        
        if rating_delta < -100:
            # Drop the priority exponentially if the problem is too easy for their rank
            fit_score -= (abs(rating_delta) / 40) ** 2  
        elif rating_delta > 200:
            # Heavily penalize things beyond their reach to preserve a realistic training curve
            fit_score -= (rating_delta / 80) ** 2
        else:
            # Reward problems sitting perfectly in their competitive growth zone
            fit_score += 2.0
            # Small calibration bonus if it introduces a brand new topic at a safe level
            if has_untouched_topic and rating_delta <= 50:
                fit_score += 1.0
                
        scored_candidates.append((prob, prob_tags, fit_score))
        
    # Sort candidates by final calculated adaptive training score
    scored_candidates.sort(key=lambda x: x[2], reverse=True)
    


    recommendations_output = []
    topic_counts = {}  # Map to prevent single-topic monopolies
    
    for prob, tags, _ in scored_candidates:
        if len(recommendations_output) >= 5:
            break
            
        embedded_mastery = {t: round(mastery.get(t, 0.0), 3) for t in tags}
        weak_topics = [t for t, s in embedded_mastery.items() if s < 0.4]
        primary_weakness = weak_topics[0] if weak_topics else tags[0]
        
        # THEMATIC DIVERSITY CAP: Limit any weak area to maximum 2 slots
        if topic_counts.get(primary_weakness, 0) >= 2:
            continue
            
        topic_counts[primary_weakness] = topic_counts.get(primary_weakness, 0) + 1
        
        recommendations_output.append({
            "title": prob["title"],
            "titleSlug": prob["titleSlug"],
            "difficulty": prob["difficulty"],
            "cf_rating": prob["cf_rating"],
            "acRate": prob["acRate"],
            "url": prob["url"],
            "topicTags": tags,
            "why_recommended": f"Targets your weak areas: {primary_weakness}",
            "your_mastery_in_topic": embedded_mastery
        })
        

    final_response = {
        "mastery_endpoint_preview": {
            "username": handle,
            "current_rating": current_rating,
            "growth_velocity": round(velocity, 3),
            "status": "improving" if velocity >= 0.5 else "stable",
            "topics": [
                {"topic": t, "mastery": round(s, 3), "level": map_mastery_level(s)}
                for t, s in mastery.items()
            ]
        },
        "recommendations": recommendations_output
    }
    
    # return final_response 
    
    # out_file = f"{handle}_prod_contract.json"
    # with open(out_file, "w") as f:
    #     json.dump(final_response, f, indent=2)
        
    # print(f"\n[success] Balanced Realistic Payload generated at: {out_file}\n")
    return final_response 
    # print(json.dumps(final_response, indent=2))
    # return out_file

if __name__ == "__main__":
    handle = input("Enter Codeforces handle for validation test: ").strip()
    generate_production_payload(handle)