from analytics.scoring import calculate_scores


def compare_startups(report_a, report_b):

    score_a = calculate_scores(report_a)

    score_b = calculate_scores(report_b)

    if score_a["overall"] > score_b["overall"]:
        winner = "Startup A"

    elif score_b["overall"] > score_a["overall"]:
        winner = "Startup B"

    else:
        winner = "Tie"

    return {
        "startup_a": score_a,
        "startup_b": score_b,
        "winner": winner
    }