from lib.s3_analyzer_v2 import S3_analyzer
from lib.ebs_analyzer import ebs_analyzer

s3 = S3_analyzer()

## Specifiy regions to analyze
regions = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'ca-central-1',
    'eu-west-1',
    'eu-west-2',
    'eu-central-1'
]

# ## Creates report showing Region, Size, Encryption, age and monthly cost
# ## Exports: CSV
print("EBS: Analyzing...")
ebs = ebs_analyzer(regions)
ebs.analyze()

## Creates report showing Region, Size, Number of Objects, Potential Costs, Lifecycle Policys, Replication Policies
## Exports: CSV, HTML
print("S3: Analyzing...")
s3.analyze()
