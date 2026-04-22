import csv
from pathlib import Path


def write_csv(file_path, headers, rows, progress_callback=None, progress_step=100):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(headers)

        count = 0

        for row in rows:
            writer.writerow(row)

            count += 1

            if progress_callback and count % progress_step == 0:
                progress_callback(count)

        if progress_callback:
            progress_callback(count)


def write_csv_paged(
    file_path,
    headers,
    fetch_page,
    *,
    page_size=1000,
    progress_callback=None,
    progress_step=100,
):
    """
    Write a CSV by paging data via fetch_page(offset, limit) -> list[rows].

    Avoids streaming DB cursors so callers can safely commit progress mid-export.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        count = 0
        offset = 0

        while True:
            rows = fetch_page(offset, page_size)
            if not rows:
                break

            for row in rows:
                writer.writerow(row)
                count += 1
                if progress_callback and count % progress_step == 0:
                    progress_callback(count)

            offset += len(rows)

        if progress_callback:
            progress_callback(count)
