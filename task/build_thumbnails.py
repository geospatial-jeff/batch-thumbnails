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

def build_thumbnails(input_bucket, input_key):
    tempdir = tempfile.mkdtemp()

    content_object = s3_res.Object(input_bucket, input_key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    payload = json.loads(file_content)

    sys.stdout.write(f"Building thumbnails for {len(payload['images'])} images.")
    sys.stdout.flush()

    for file in payload['images']:
        infile = file['input']
        out_bucket = file['out_bucket']
        out_key = file['out_key']
        xsize = file['xsize']
        ysize = file['ysize']
        temppath = os.path.join(tempdir, str(uuid.uuid4()))

        # Create JPEG preview
        subprocess.call(f'gdal_translate {infile} {temppath} -of JPEG -ot Byte -outsize {xsize} {ysize}', shell=True)

        # Upload to target bucket/key
        s3_res.Object(out_bucket, out_key).upload_file(temppath)

    sys.stdout.write(f"Finished building thumbnails.")
    sys.stdout.flush()

    shutil.rmtree(tempdir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('input_bucket')
    ap.add_argument('input_key')
    args = ap.parse_args()

    build_thumbnails(args.input_bucket, args.input_key)

