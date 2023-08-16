from lib.cost_s3 import S3_analyzer

s3 = S3_analyzer()

print("S3: Analyzing...")
s3.analyze()
s3.html()
