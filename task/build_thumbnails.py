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

def build_thumbnail(input_bucket, input_key):
    tempdir = tempfile.mkdtemp()
    content_object = s3_res.Object(input_bucket, input_key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    payload = json.loads(file_content)

    item_to_process = payload['images'][int(os.getenv('AWS_BATCH_JOB_ARRAY_INDEX'))]
    infile = item_to_process['input']
    out_bucket = item_to_process['out_bucket']
    out_key = item_to_process['out_key']
    xsize = item_to_process['xsize']
    ysize = item_to_process['ysize']
    temppath = os.path.join(tempdir, str(uuid.uuid4()))

    # Create JPEG preview
    subprocess.call(f'gdal_translate {infile} {temppath} -of JPEG -ot Byte -outsize {xsize} {ysize}', shell=True)

    # Upload to target bucket/key
    s3_res.Object(out_bucket, out_key).upload_file(temppath)

    shutil.rmtree(tempdir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('input_bucket')
    ap.add_argument('input_key')
    args = ap.parse_args()

    build_thumbnail(args.input_bucket, args.input_key)

