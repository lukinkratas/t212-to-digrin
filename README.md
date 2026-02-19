# T212 to Digrin

Automation of Trading 212 portfolio analytics in Digrin.

Monthly report is then transformed for Digrin and stored in AWS S3.
Can be run from CLI or AWS lambda.

![cli](doc/cli.png)

1. (CLI only) Get input year_month.
2. [T212 rest API calls](https://docs.trading212.com/api) to gen export and list reports endpoints with creds stored in AWS Secrets Manager.
3. Download raw T212 CSV report and store it in AWS S3 via boto SDK.
4. Transform the report to Digrin form and store it in AWS S3 via boto SDK.
5. (CLI only) Download locally.
6. (Lambda only) Generate S3 presigned URL for download via boto SDK.
6. (Lambda only) Send email with presigned URL via AWS SES.

### Technical Overview

- AWS services used - IAM, S3, Lambda, EventBridge Scheduler, Secrets Manager, SES
- IaC via Terraform
- CICD for testing and deployment via GH actions
- Unit tests via pytest

### CLI Run

**Requirements:** `aws configure --profile t212-to-digrin-cli`

```bash
uv run python -m t212_to_digrin
```
