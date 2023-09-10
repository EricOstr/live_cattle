import boto3


def main():

    # Replace with your S3 bucket name, object key, and desired local filename
    bucket_name = 'eriostri-testing'
    object_key = 'report.pdf'
    local_filename = '/Users/ericostring/Desktop/local.pdf'

    # Retrieve the S3 object
    s3 = boto3.client('s3')

    s3.download_file(bucket_name, object_key, local_filename)


    pass

if __name__ == "__main__":
    main()
