# import boto3
# import time

# def start_document_text_detection(client, bucket, document):
#     # Start the text detection job
#     response = client.start_document_text_detection(
#         DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': document}}
#     )

#     # Get the JobId from the response
#     job_id = response['JobId']
    
#     return job_id

# def check_job_status(client, job_id):
#     while True:
#         # Check the status of the text detection job
#         response = client.get_document_text_detection(JobId=job_id)
#         status = response['JobStatus']
        
#         if status in ['SUCCEEDED', 'FAILED']:
#             break
        
#         # Wait before checking again (adjust the sleep duration as needed)
#         time.sleep(5)

#     return response

# def main():
#     client = boto3.client('textract')  # Replace with your desired region
#     bucket = 'eriostri-us-east-1'
#     document = 'report.pdf'

#     # Start the text detection job and get the JobId
#     job_id = start_document_text_detection(client, bucket, document)

#     # Check the status of the job and retrieve the results
#     response = check_job_status(client, job_id)

#     # Process the response
#     for item in response['Blocks']:
#         if item['BlockType'] == 'LINE':
#             print(item['Text'])

# if __name__ == "__main__":
#     main()





import boto3

def process_text_detection(client, bucket, document):

 

    return response

def main():
    session = boto3.Session()
    client = session.client('textract')
    bucket = 'eriostri-us-east-1'
    document = 'report.pdf'

    response = client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': document}})

    pass

if __name__ == "__main__":
    main()
