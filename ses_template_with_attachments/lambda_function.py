import json
import os
import sys
import traceback

from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from email_composer import Email

def lambda_handler(event, context):

    try:

        email = Email(event)
        email.generator_wrapper()
        email.send_email()

    return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"}
            "body": json.dumps("Hello from Lambda!")
            }


    except Exception as e:
        print("Error in main try/except of sendEmail")
        print(e)
        traceback.print_exc()
        sys.exit(1)
