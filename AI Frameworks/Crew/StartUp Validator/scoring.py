def calculate_scores(report):

    text = str(report).lower()

    demand = 5
    revenue = 5
    risk = 5

    positive_keywords = [
        "growth",
        "opportunity",
        "market",
        "demand",
        "revenue",
        "profit",
        "scalable",
        "potential",
        "customers",
        "expansion"
    ]

    negative_keywords = [
        "risk",
        "competition",
        "challenge",
        "threat",
        "problem",
        "difficult"
    ]

    for word in positive_keywords:

        if word in text:
            demand += 1
            revenue += 1

    for word in negative_keywords:

        if word in text:
            risk -= 1

    demand = max(1, min(10, demand))
    revenue = max(1, min(10, revenue))
    risk = max(1, min(10, risk))

    overall = round(
        (demand + revenue + risk) / 3,
        1
    )

    return {
        "demand": demand,
        "revenue": revenue,
        "risk": risk,
        "overall": overall
    }