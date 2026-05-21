# Automatic Photo Organizer

Automatically renames and organizes photos and videos synced to a NAS or local folder. Files are renamed using their metadata and sorted into year folders. Designed to run continuously as a Docker container.

---

## How It Works

APO watches an `unsorted` folder on a timer. When files are found it reads their metadata using [ExifTool](https://exiftool.org), builds a new filename, copies the file to the `sorted` folder, and deletes the original.

### File Naming

Files are renamed using the pattern `YYYY-MM-DD.HHMMSS.Location.ext`.

**Timestamp** is read from EXIF/QuickTime metadata in priority order. If no metadata timestamp is found, APO attempts to parse a date from the original filename.

**Location** is resolved by looking up the GPS coordinates in the file's metadata using the [Nominatim](https://nominatim.org) OpenStreetMap API (zoom level 10, which returns city or county). If no GPS data is present the location is omitted. To respect the Nominatim usage policy there is a 1.5 second delay between each GPS lookup.

**Duplicates** — files that would produce the same name get a numeric counter appended: `.1`, `.2`, `.3`, etc. The counter uses only as many digits as the group requires (e.g. 9 duplicates use `1–9`, 10+ use `01–10`, etc.). Files with no duplicates have no counter at all.

**Examples:**
```
2023-07-25.143521.Paris.jpg          ← single file, no counter
2023-07-25.143523.Paris.1.jpg        ← first of several taken at the same time/place
2023-07-25.143523.Paris.2.jpg
2017-10-01.111108.Hawaii_County.jpg  ← county used when no city is found
2004-03-20.143659.jpg                ← no GPS data, no location
2006-10-31.jpg                       ← date parsed from filename, no time available
```

### Folder Structure

Sorted files are placed in year subfolders:

```
sorted/
├── 2023/
│   ├── 2023-07-25.143521.Paris.jpg
│   ├── 2023-07-25.143521.Paris.1.jpg
│   └── 2023-07-25.143521.Paris.2.jpg
└── 2007/
    ├── 2007-12-24.080149.Mesa.jpg
    └── 2007-12-24.080150.Mesa.jpg
```

### Skipped Files

Files that cannot be processed are tracked in `skipped.yaml` (in the APO app folder) with a reason and a skip count:

```yaml
/data/unsorted/photo.jpg:
  reason: gps_failure
  skip_count: 2
```

There are three skip reasons:

| Reason | Behaviour |
|---|---|
| `gps_failure` | Retried each run. Once `GPS_RETRY_LIMIT` is reached the file is processed without location data. |
| `no_timestamp` | Skipped permanently. The file has no usable date in its metadata or filename. |
| `no_extension` | Skipped permanently. The file has no extension. |

A timestamped snapshot of `skipped.yaml` is also copied to the logs folder at the end of every run so you can track how the skip list changes over time.

---

## Logs

A new log file is created for every run, named by the time the run started: `2024-03-15_14-30.log`. The matching skip snapshot for that run is saved alongside it as `2024-03-15_14-30.skipped.yaml`. Both files are cleaned up together when the log limit is reached.

Log files are written to the `logs` path (default `/data/logs`).

---

## Docker Setup

**Minimum Docker CLI:**
```bash
docker run \
  -v /path/to/unsorted:/data/unsorted \
  -v /path/to/sorted:/data/sorted \
  jeremytoler/auto_photo_org:latest
```

**Docker Compose with all options:**
```yaml
services:
  auto_photo_org:
    image: jeremytoler/auto_photo_org:latest
    restart: unless-stopped
    environment:
      - WAIT_TIME_MINUTES=1440   # How often to scan, in minutes. Default: 1440 (24 hours)
      - MAX_LOGS=100             # Number of runs to keep logs for. Default: 100
      - GPS_RETRY_LIMIT=3        # GPS failures before processing without location. Default: 3
      - RENUMBER_ALL=false       # Re-apply numbering to all sorted files on startup. Default: false
      - UNSORTED_PATH=/data/unsorted  # Override default input path
      - SORTED_PATH=/data/sorted      # Override default output path
      - LOGS_PATH=/data/logs          # Override default logs path
    volumes:
      - /path/to/unsorted:/data/unsorted
      - /path/to/sorted:/data/sorted
      - /path/to/logs:/data/logs
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `WAIT_TIME_MINUTES` | `1440` | Minutes between scans (1440 = 24 hours) |
| `MAX_LOGS` | `100` | Number of runs to retain logs for. Oldest run's `.log` and `.skipped.yaml` are deleted together. |
| `GPS_RETRY_LIMIT` | `3` | Number of times a GPS failure is retried before the file is sorted without location data. |
| `UNSORTED_PATH` | `/data/unsorted` | Path to the folder APO watches for new files. |
| `SORTED_PATH` | `/data/sorted` | Path to the folder APO sorts files into. |
| `LOGS_PATH` | `/data/logs` | Path to the folder logs are written to. |

---

## Running Locally (Without Docker)

Requires Python 3.12+ and [ExifTool](https://exiftool.org) installed and on your `PATH`.

**Install dependencies:**
```cmd
pip install -r requirements.txt
```

**Set paths and run (Windows cmd):**
```cmd
set UNSORTED_PATH=C:\path\to\unsorted
set SORTED_PATH=C:\path\to\sorted
set LOGS_PATH=C:\path\to\logs
set WAIT_TIME_MINUTES=2
python D:\path\to\auto_photo_org\apo\apo_file_scan.py
```

**Set paths and run (PowerShell):**
```powershell
$env:UNSORTED_PATH = "C:\path\to\unsorted"
$env:SORTED_PATH   = "C:\path\to\sorted"
$env:LOGS_PATH     = "C:\path\to\logs"
$env:WAIT_TIME_MINUTES = "2"
python D:\path\to\auto_photo_org\apo\apo_file_scan.py
```

All environment variables from the table above work the same way locally. `set` / `$env:` variables only last for the current terminal session.

---

## Troubleshooting

**Files not being sorted** — Check the latest `.log` file in your logs folder. Every skipped file is logged with its full path and the reason it was skipped. Check `skipped.yaml` in the logs folder to see all currently pending files and their skip counts.

**GPS not resolving** — Nominatim is a free public API with a strict rate limit. APO waits 1.5 seconds between requests to stay within it, but the service can still be intermittently unavailable. Affected files are retried automatically each run. After `GPS_RETRY_LIMIT` failures they are sorted without location data.

**Files with no date** — If a file has no EXIF timestamp and the date cannot be parsed from the filename it will be added to `skipped.yaml` with reason `no_timestamp`. These files will not be retried automatically and will need to be manually reviewed.

Feel free to open an issue if a file is being renamed incorrectly. Please include the original filename and the relevant section of the log file.
