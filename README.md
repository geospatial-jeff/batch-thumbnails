# batch-thumbnails
Generate image thumbnails on AWS Batch

# Installation
1. Clone the library.
2. Add subnet-ids and vpc-ids to `serverless.yml`
3. Change other configuration options as needed.
4. Deploy with `sls deploy -v`

# Usage
Kick off the service by uploading a JSON file to the ingest s3 bucket.  The service expects the following payload:

```json
{
  "images": [
    {
      "input": "/vsicurl/https://path/to/input.tif",
      "out_bucket": "thumbnail-outputs",
      "out_key": "path/to/thumbnail.jpg",
      "xsize": 270,
      "ysize": 270
    }
  ]
}
```

This payload tells AWS Batch to generate a 270x270 pixel thumbnail of `https://path/to/input.tif` and save to `s3://thumbnail-outputs/path/to/thumbnail.jpg`.  The `images` key may contain either a list of dictionaries or a nested list of dictionaries (for micro-batching multiple messages in each array job).

### Best Practices
The time to create an individual thumbnail will vary widely depending on a number of factors.  Regardless of the speed, it's important to ensure that each job in the array receives enough images to run continuously for 3-5 minutes to maximize the time spent processing vs spinning up new jobs.