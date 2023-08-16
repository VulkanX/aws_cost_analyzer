import boto3
import datetime
import csv


#Create S3 Class
class S3_analyzer:

    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.all_buckets = []

    def analyze(self):
        # Initialize AWS credentials and S3 client
        s3_client = boto3.client('s3')

        # List all S3 buckets in the account
        response = s3_client.list_buckets()
        buckets = response['Buckets']

        # Calculate potential cost savings based on object age and storage type
        current_date = datetime.datetime.now().astimezone()

        # AWS S3 Tier Cost table: https://aws.amazon.com/s3/pricing/
        aws_s3_pricing = {
            'STANDARD': 0.023,
            'INTELLIGENT_TIERING': 0.023,
            'STANDARD_IA': 0.0125,
            'ONEZONE_IA': 0.01,
            'GLACIER': 0.004,
            'DEEP_ARCHIVE': 0.00099
        }

        for bucket in buckets:
            bucket_name = bucket['Name']
            print(f"Processing bucket: {bucket_name}")

            # Total Cost of the bucket as an object so we can store each tier's cost
            bucket_cost = {
                'STANDARD': 0.0,
                'INTELLIGENT_TIERING': 0.0,
                'STANDARD_IA': 0.0,
                'ONEZONE_IA': 0.0,
                'GLACIER': 0.0,
                'DEEP_ARCHIVE': 0.0
            }

            bucket_items = {
                'STANDARD': 0,
                'INTELLIGENT_TIERING': 0,
                'STANDARD_IA': 0,
                'ONEZONE_IA': 0,
                'GLACIER': 0,
                'DEEP_ARCHIVE': 0
            }

            # Get S3 objects
            objects = s3_client.list_objects_v2(Bucket=bucket_name)

            # Get S3 bucket lifecycle
            try:
                lifecycle = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name,)['Rules'][0]['ID']
            except Exception as e:
                lifecycle = "No"

            if 'Contents' in objects:
                # Add up the whole bucket cost
                total_cost = 0
                total_size = 0
                for obj in objects['Contents']:
                    key = obj['Key']
                    last_modified = obj['LastModified']
                    storage_class = obj['StorageClass']

                    # Calculate the age of the object
                    # print(f" - {key} - {storage_class} - {last_modified}")
                    age = (current_date - last_modified).days

                    # Convert Object size from Bytes to GB
                    obj['Size'] = obj['Size'] / 1024 / 1024 / 1024
                    total_size += obj['Size']

                    # # Store base cost of object
                    current_cost = obj['Size'] * aws_s3_pricing[storage_class]
                    total_cost += current_cost

                    # Track how many items are in each tier
                    bucket_items[storage_class] += 1

                    # If age is greater than 90 days then calculate the potential savings for each storage tier calculate the total for the bucket for each tier
                    if age >= 90:
                        # Loop through all pricing tiers and calculate pricing differences
                        for tier in aws_s3_pricing:
                            # If the current Tier is the current object's tier then the cost is 0
                            if tier == storage_class:
                                bucket_cost[tier] += 0
                            # If Tier is higher than the current tier then add the difference in cost to the cost of the tier
                            else:
                                bucket_cost[tier] += obj['Size'] * (aws_s3_pricing[storage_class] - aws_s3_pricing[tier])

                # Store the bucket name and cost in the list of all buckets
                self.all_buckets.append({
                    "bucket": bucket_name,
                    "items": len(objects['Contents']),
                    "size": total_size,
                    "cost": total_cost,
                    "lifecycle": lifecycle,
                    "savings": bucket_cost,
                    "itemtotals": bucket_items}
                )


        print("Calculating totals for all buckets")
        # Total up each tier seperately for all buckets and store it as a total line in the object
        bucket_totals = {
            'STANDARD': 0.0,
            'INTELLIGENT_TIERING': 0.0,
            'STANDARD_IA': 0.0,
            'ONEZONE_IA': 0.0,
            'GLACIER': 0.0,
            'DEEP_ARCHIVE': 0.0
        }
        bucket_item_totals = {
            'STANDARD': 0,
            'INTELLIGENT_TIERING': 0,
            'STANDARD_IA': 0,
            'ONEZONE_IA': 0,
            'GLACIER': 0,
            'DEEP_ARCHIVE': 0
        }
        item_total = 0 
        size_total = 0
        cost_total = 0

        for bucket in self.all_buckets:
            for tier in bucket['savings']:
                bucket_totals[tier] += bucket['savings'][tier]
            for tier in bucket['itemtotals']:
                bucket_item_totals[tier] += bucket['itemtotals'][tier]
            item_total += bucket['items']
            size_total += bucket['size']
            cost_total += bucket['cost']

        # Sort buckets by cost
        self.all_buckets.sort(key=lambda x: x['cost'], reverse=True)

        self.all_buckets.append({
            "bucket": "Total",
            "items": item_total,
            "size": size_total,
            "cost": cost_total,
            "lifecycle": "",
            "savings": bucket_totals,
            "itemtotals": bucket_item_totals})

    def html(self):
        html = "<html><head>"
        html += "<title>S3 Storage Cost Analysis</title>"
        html += """<style>
                        table, th, td {
                            border: 1px solid black;
                            border-collapse: collapse;
                            }
                        td, th {padding: 5px;}
                        tbody tr:nth-child(odd) {background-color: #cccccc;}
                        tbody tr:nth-child(even) {background-color: #eeeeee;}
                    </style>"""
        html += "</head><body>"
        html += "<h1>S3 Cost Savings Analysis</h1>"
        html += "<table>"


        # Generate HTML Table Header
        html += "<tr>"
        html += "<th>Bucket</th>"
        html += "<th>Items</th>"
        html += "<th>Size (GB)</th>"
        html += "<th>Cost</th>"
        html += "<th>Lifecycle</th>"
        html += "<th>Items</th>"
        html += "<th>STANDARD</th>"
        html += "<th>Items</th>"
        html += "<th>INTELLIGENT</th>"
        html += "<th>Items</th>"
        html += "<th>IA</th>"
        html += "<th>Items</th>"
        html += "<th>ONEZONE</th>"
        html += "<th>Items</th>"
        html += "<th>GLACIER</th>"
        html += "<th>Items</th>"
        html += "<th>DEEP ARCHIVE</th>"
        html += "</tr>"

        # Generate HTML Table Rows
        for bucket in self.all_buckets:
            html += "<tr>"
            html += f"<td>{bucket['bucket']}</td>"
            html += f"<td>{bucket['items']}</td>"
            html += f"<td>{bucket['size']:.2f}</td>"
            html += f"<td>{bucket['cost']:.5f}</td>"
            html += f"<td>{bucket['lifecycle']}</td>"
            html += f"<td>{bucket['itemtotals']['STANDARD']}</td>"
            html += f"<td>{bucket['savings']['STANDARD']:.5f}</td>"
            html += f"<td>{bucket['itemtotals']['INTELLIGENT_TIERING']}</td>"
            html += f"<td>{bucket['savings']['INTELLIGENT_TIERING']:.5f}</td>"
            html += f"<td>{bucket['itemtotals']['STANDARD_IA']}</td>"
            html += f"<td>{bucket['savings']['STANDARD_IA']:.5f}</td>"
            html += f"<td>{bucket['itemtotals']['ONEZONE_IA']}</td>"
            html += f"<td>{bucket['savings']['ONEZONE_IA']:.5f}</td>"
            html += f"<td>{bucket['itemtotals']['GLACIER']}</td>"
            html += f"<td>{bucket['savings']['GLACIER']:.5f}</td>"
            html += f"<td>{bucket['itemtotals']['DEEP_ARCHIVE']}</td>"
            html += f"<td>{bucket['savings']['DEEP_ARCHIVE']:.5f}</td>"
            html += "</tr>"

        html += "</table></body></html>"

        # Write HTML to file
        with open('s3.html', 'w') as htmlfile:
            htmlfile.write(html)

    def csv(self):
        # Generate CSV Data and export
        print("Generating CSV Data")
        csv_data = []
        for bucket in self.all_buckets:
            csv_data.append(
                [bucket['bucket'],
                bucket['items'],
                bucket['size'],
                bucket['cost'],
                bucket['lifecycle'],
                bucket['itemtotals']['STANDARD'],
                bucket['savings']['STANDARD'],
                bucket['itemtotals']['INTELLIGENT_TIERING'],
                bucket['savings']['INTELLIGENT_TIERING'],
                bucket['itemtotals']['STANDARD_IA'],
                bucket['savings']['STANDARD_IA'],
                bucket['itemtotals']['ONEZONE_IA'],
                bucket['savings']['ONEZONE_IA'],
                bucket['itemtotals']['GLACIER'],
                bucket['savings']['GLACIER'],
                bucket['itemtotals']['DEEP_ARCHIVE'],
                bucket['savings']['DEEP_ARCHIVE']]
            )

        with open('s3.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "Bucket",
                "Items",
                "Size (GB)",
                "Cost",
                "Lifecycle",
                "STANDARD Items",
                "STANDARD",
                "INTELLIGENT_TIERING Items",
                "INTELLIGENT_TIERING",
                "STANDARD_IA Items",
                "STANDARD_IA",
                "ONEZONE_IA Items",
                "ONEZONE_IA",
                "GLACIER Items",
                "GLACIER",
                "DEEP_ARCHIVE Items",
                "DEEP_ARCHIVE"]
            )
            writer.writerows(csv_data)    