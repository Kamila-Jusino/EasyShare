# adapted to fit snippet from https://repost.aws/knowledge-center/lambda-send-email-ses used in lambda function
import boto3
import json
from flask import Flask, render_template, request
################################################
# starts flask application
app = Flask(__name__)
############################################
# s3,Lambda,dynamo (region name added to help with EC2 instance failures-- for my debugging purposes)
s3 = boto3.client('s3', region_name='us-east-1')
lambda_client = boto3.client('lambda', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
BUCKET_NAME = 'easyshare-kamila'
TABLE_NAME = 'Easy_Share'  
table = dynamodb.Table(TABLE_NAME)
#################################################
# for html page 
@app.route('/')
def index():
    return render_template('index.html')
###############################################
# file upload
@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files.get('file')
    
    # for my debugging purposes
    collected_emails = []
    for i in range(1, 6):
        email = request.form.get(f'email{i}')
        if email:
            collected_emails.append(email)

    share_with = collected_emails  
#############################################
    if uploaded_file:
        # upload to s3 bucket
        s3.upload_fileobj(uploaded_file, BUCKET_NAME, uploaded_file.filename)
        # metadata into DynamoDB (view below for documentation)
        table.put_item(
            Item={
                'FileName': uploaded_file.filename,
                'SharedWith': share_with
            }
        )
        # triger for Lambda function 
        lambda_payload = {
            "share_with": share_with,
            "bucket_name": BUCKET_NAME,
            "object_key": uploaded_file.filename
        }
        lambda_response = lambda_client.invoke(
            FunctionName='myFunction',
            InvocationType='RequestResponse',
            Payload=json.dumps(lambda_payload)
        )
    return render_template('index.html')
#########################################
# start the Flask application on all network interfaces
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# notes for myself (documentation links): 
# https://flask.palletsprojects.com/en/stable/installation/#python-version
# https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
# https://medium.com/hackernoon/using-aws-dynamodb-with-flask-9086c541e001
