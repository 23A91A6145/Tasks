import tempfile
import subprocess
import os


def run_bandit(code):

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".py",
            mode="w",
            encoding="utf-8"
        ) as f:

            f.write(code)

            filename = f.name

        result = subprocess.run(
            [
                "bandit",
                "-r",
                filename
            ],
            capture_output=True,
            text=True
        )

        os.unlink(filename)

        return result.stdout

    except Exception as e:

        return str(e)