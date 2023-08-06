from typing import Any

import tqdm


def update_progress_bar(t: tqdm.tqdm) -> Any:
    """Updates the progress of a tqdm progress bar.
    This method will be passed to the callback argument of the s3 download_file/
    upload file methods"""

    def inner(bytes_amount):
        t.update(bytes_amount)

    return inner
