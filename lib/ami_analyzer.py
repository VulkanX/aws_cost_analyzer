import boto3
import datetime
import csv


class ami_analyzer:

    def __init__(self, region_list=['us-east-1']):
        self.images = []
        self.region_list = region_list

    def analyze(self):
        print ("AMI: Analyzing...")

        # Loop through Regions
        for region in self.region_list:

            # Pull all AMI's from the region
            ami = boto3.client('ec2', region_name=region)
            images = ami.describe_images(Owners=['self'])['Images']

            # Determine age and cost of each AMI by adding storage
            for image in images:
                image_encryption = False
                image_platform = image['PlatformDetails']
                image_id = image['ImageId']
                image_creation_date = image['CreationDate']
                image_creation_date = datetime.datetime.strptime(image_creation_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                image_age = datetime.datetime.now() - image_creation_date

                image_storage_cost = 0
                for block_device in image['BlockDeviceMappings']:
                    if 'Ebs' in block_device:
                        image_storage_cost += block_device['Ebs']['VolumeSize'] * 0.05
                    if 'Encrypted' in block_device:
                        image_encryption = block_device['Encrypted']

                self.images.append({
                    'Region': region,
                    'Name': image['Name'],
                    'Description': image['Description'],
                    'Platform': image_platform,
                    'ImageId': image_id,
                    'ImageCost': image_storage_cost,
                    'ImageAge': image_age.days,
                    'ImageEncryption': image_encryption,
                })
        self.csv()

    def csv(self):
        # Write CSV
        with open('ami.csv', 'w', newline='') as csvfile:
            fieldnames = ['Region', 'Name', 'Description', 'Platform', 'ImageId', 'ImageCost', 'ImageAge', 'ImageEncryption']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for image in self.images:
                writer.writerow(image)
