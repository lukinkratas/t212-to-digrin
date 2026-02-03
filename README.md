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

**Requirements**:
- T212 api key (only all history perms)
- T212 api key in AWS Secrets Manager.
- configure AWS CLI via `aws configure` (or use .env)

### Run

```bash
    uv run python -m t212_to_digrin
```

# TODO
- [ ] add unit tests with mocking
- [ ] format and lint
- [x] why is not get_input_dt logger? -> NOPE
- [ ] warning / err log record formatting
- [ ] AWS tags, resource group, application (after terraform)
- [ ] presigned url only in CLI, lambda not
