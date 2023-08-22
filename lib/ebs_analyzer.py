import boto3
import datetime
import csv


class ebs_analyzer:

    def __init__(self, region_list=['us-east-1']):
        self.snapshots = []
        self.region_list = region_list

    def analyze(self):

        # Loop through Regions
        for region in self.region_list:        

            # Initialize AWS credentials and S3 client
            ebs = boto3.client('ec2', region_name=region)
            snapshots = ebs.describe_snapshots(OwnerIds=['self'])['Snapshots']

            # Flag Snapshots over 30 days old
            for snapshot in snapshots:
                snapshot_id = snapshot['SnapshotId']
                snapshot_start_time = snapshot['StartTime']
                snapshot_start_time = snapshot_start_time.replace(tzinfo=None)
                snapshot_age = datetime.datetime.now() - snapshot_start_time

                self.snapshots.append({
                    'Region': region,
                    'SnapshotId': snapshot_id,
                    'SnapshotSize': snapshot['VolumeSize'],
                    'SnapshotCost': snapshot['VolumeSize'] * 0.05,
                    'SnapshotAge': snapshot_age.days,
                    'StorageTier': snapshot['StorageTier'],
                    'SnapshotEncryption': snapshot['Encrypted'],
                })
        self.csv()



    def csv(self):
        # Write CSV
        with open('ebs.csv', 'w', newline='') as csvfile:
            fieldnames = ['Region', 'SnapshotId', 'SnapshotSize', 'SnapshotCost', 'SnapshotAge', 'StorageTier', 'SnapshotEncryption']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for snapshot in self.snapshots:
                writer.writerow(snapshot)