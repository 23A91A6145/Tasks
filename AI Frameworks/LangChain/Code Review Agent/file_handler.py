from pathlib import Path


UPLOAD_DIR = Path(
    "uploads"
)

UPLOAD_DIR.mkdir(
    exist_ok=True
)


def save_uploaded_file(
    uploaded_file
):

    file_path = (
        UPLOAD_DIR /
        uploaded_file.name
    )

    with open(
        file_path,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )

    return str(file_path)