import os
import boto3

batch_client = boto3.client('batch')

JOB_DEFINITION = os.getenv('JOB_DEFINITION')
JOB_QUEUE = os.getenv('JOB_QUEUE')

def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    args = {
        'jobName': os.path.splitext(os.path.split(key)[-1]),
        'jobQueue': JOB_QUEUE,
        'jobDefinition': JOB_DEFINITION,
        'parameters': {
            'in_bucket': bucket,
            'in_key': key
        }
    }

    batch_client.submit_job(**args)