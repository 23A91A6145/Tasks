def parse_plan(text: str):

    steps = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line[0].isdigit():

            line = line.split(".", 1)[1].strip()

            steps.append(line)

    return steps