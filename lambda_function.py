# code adapted from https://repost.aws/knowledge-center/lambda-send-email-ses
# documentation used:
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
import json
import boto3
###############################################
client = boto3.client('ses', region_name='us-east-1')
def lambda_handler(event, context):
    try:
        sender = 'kamila.jusino@gmail.com'
        share_with = event.get('share_with', [])
        bucket_name = event.get('bucket_name')
        object_key = event.get('object_key')  
###################################################       
        s3_client = boto3.client('s3', region_name='us-east-1')
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=3600  
        )
        response = client.send_email(
            Source=sender,
            Destination={'ToAddresses': share_with},
            Message={
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': 'You have received a file'
                },
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': (
                         f'A file was shared with you using EasyShare.\n'
                         f'View link below:\n{presigned_url}\n'
                         'Link epires in 1 hour'
                        )
                    }
                }
            }                        
        )
        return {
            'statusCode': 200,
            'body': json.dumps("Email sent Successfully. Message ID: " + response['MessageId'])
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error sending email: {str(e)}")
        }
