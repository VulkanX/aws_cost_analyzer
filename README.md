# AWS Cost Analyzer Scripts

these are not ment to be hard suggetions for costs savings but analysis and data to allow someone with knowledge of AWS and the data to make better decisions around cost savings and storage changes

## Pre requisits
This does not use stored credentials and uses whatever credentials you are currently using on the CLI so be sure to assume another role or set the right profile to default for the AWS CLI tools

### S3 Analyzer
S3 analyzer scans all buckets, checks for lifecycle policies and does a quick inventory of how many items are in each storage tier and calculates savings costs based on access greater than 90 days. Pricing is currently based off us-east-1 (N. Virginia) and does not take into account 50tb+ discounts

Note that this script is only looking at raw storage costs and not transfer costs.

