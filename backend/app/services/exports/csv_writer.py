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
