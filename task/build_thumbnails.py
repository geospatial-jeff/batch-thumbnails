import argparse
import json
import tempfile
import subprocess
import uuid
import shutil
import os
import sys

import boto3

s3_res = boto3.resource('s3')

def process_job(input_bucket, input_key):
    tempdir = tempfile.mkdtemp()

    content_object = s3_res.Object(input_bucket, input_key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    payload = json.loads(file_content)

    array_value = payload['images'][int(os.getenv('AWS_BATCH_JOB_ARRAY_INDEX'))]

    # Allow for micro-batching
    if type(array_value) is list:
        for item in array_value:
            build_thumbnail(item, tempdir)
    else:
        build_thumbnail(array_value, tempdir)

    shutil.rmtree(tempdir)


def build_thumbnail(job_params, tempdir):

    infile = job_params['input']
    out_bucket = job_params['out_bucket']
    out_key = job_params['out_key']
    xsize = job_params['xsize']
    ysize = job_params['ysize']
    temppath = os.path.join(tempdir, str(uuid.uuid4()))

    # Create JPEG preview
    subprocess.call(f'gdal_translate {infile} {temppath} -of JPEG -ot Byte -outsize {xsize} {ysize}', shell=True)

    # Upload to target bucket/key
    s3_res.Object(out_bucket, out_key).upload_file(temppath)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('input_bucket')
    ap.add_argument('input_key')
    args = ap.parse_args()

    build_thumbnail(args.input_bucket, args.input_key)

