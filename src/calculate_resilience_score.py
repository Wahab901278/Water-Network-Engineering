def resilience_score(before_metrics, after_metrics):
    age_improvement = before_metrics["avg_age"] - after_metrics["avg_age"]
    wsa_improvement = after_metrics["wsa"] - before_metrics["wsa"]
    pressure_cv_change = before_metrics["cv"] - after_metrics["cv"]
    score = (wsa_improvement * 100) + (age_improvement * 2) + (pressure_cv_change * 1.5)
    return score
