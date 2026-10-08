# T212 to Digrin

Simple purpose build automation script, that 1. Triggers monthly report export. 2. Downloads raw T212 CSV report and transforms it into digrin. 3. Both CSVs are uploaded to AWS S3 and digrin CSV is stored locally.

### Prerequisities

  - Fill .env file

  - Install Python

**To run:**

```bash
uv run main.py
```
