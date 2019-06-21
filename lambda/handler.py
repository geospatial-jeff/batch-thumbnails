import os
import boto3

batch_client = boto3.client('batch')

JOB_DEFINITION = os.getenv('JOB_DEFINITION')
JOB_QUEUE = os.getenv('JOB_QUEUE')

def kickoff(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    job_name = os.path.splitext(os.path.split(key)[-1])[0]

    # s3:ObjectCreated:* event source can fire two invocations for each upload
    # Make sure the job id isn't already in batch job queue
    job_status = ["SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING"]
    job_names = []
    for job in job_status:
        current_jobs = batch_client.list_jobs(jobQueue=JOB_QUEUE, jobStatus=job)
        list(map(lambda x: job_names.append(x['jobName']), current_jobs['jobSummaryList']))

    if job_name not in job_names:
        args = {
            'jobName': os.path.splitext(os.path.split(key)[-1])[0],
            'jobQueue': JOB_QUEUE,
            'jobDefinition': JOB_DEFINITION,
            "arrayProperties": {
                "size": 200
            },
            'parameters': {
                'in_bucket': bucket,
                'in_key': key
            }
        }

        batch_client.submit_job(**args)
    else:
        print(f"Job {job_name} was already submitted.")