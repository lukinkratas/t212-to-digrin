# T212 to Digrin

Python application package for exporting T212 monthly report automation via rest API calls.
Monthly report is then transformed for Digrin and stored in AWS S3.
Can be run from CLI or AWS lambda.

1. Get input year_month (CLI only).
3. POST on T212 export endpoint.
4. GET on T212 list exports endpoint.
5. Download T212 CSV report and upload it to S3.
8. Transform (to Digrin form) and upload to S3.

## CLI

### Setup

```bash
    echo "AWS_ACCESS_KEY_ID=xxx" >> .env # or use aws configure
    echo "AWS_SECRET_ACCESS_KEY=xxx" >> .env # or use aws configure
    echo "AWS_REGION=xxx" >> .env # or use aws configure
    echo "BUCKET_NAME=xxx" >> .env
    echo "T212_API_KEY=xxx" > .env
```
### Run

```bash
    uv run python -m t212_to_digrin
```

# TODO
- [ ] add unit tests with mocking
- [ ] format and lint
- [x] why is not get_input_dt logger? -> NOPE
