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

class Email:
    ''' Class to create the email object, with message and attachments
    '''

    def __init__(self, event):
        ''' Constructor for Email
        '''
        self.event = event

    def set_sender_receiver_subject(self):
        ''' Set details of sender, recipient, and subject line
        '''

        # You can set sender here manually, or pull it out of event
        # self.sender = your-address@your-domain.com
        self.SUBJECT = self.event['subject']
        self.SENDER = self.event['sender']
        self.RECIPIENT = self.event['to']

        # The AWS configuration set used to track mails
        self.CONFIGURATION_SET = "default"

    def download_files(self):
        ''' Dowload attachment files from s3
        '''
        self.attachment_filepaths = []

        if 'parsed_files' in self.event.keys():
            s3 = boto3.client('s3')
            for fpath in self.event['parsed_files']:
                outpath = f'/tmp/{Path(fpath).name}'
                bucket = 'YOUR-S3-BUCKET-NAME-HERE'
                s3.download_file(bucket, fpath, outpath)
                self.attachment_filepaths.append(outpath)

        print("Parsed filepaths to be used:")
        print(self.attachment_filepaths)

    def attach_files(self):
        ''' Add attachments to message parent container
        '''
        for index,fpath in enumerate(self.attachment_filepaths):
            # Define the attachment part and encode it using MIMEApplication.
            att = MIMEApplication(open(fpath, 'rb').read())
            # Add a header to tell the email client to treat this part as an attachment, and give the attachment a name.
            att_title = f'SET-FILE-TITLE-HERE.ext'
            att.add_header('Content-Disposition','attachment',filename=att_title)
            # Add the attachment to the parent container.
            self.msg.attach(att)

    def gen_html_body(self):
        ''' Compose the html body piece of the email
        '''

        # The HTML body of the email.
        self.BODY_HTML = f"""\
                <body>ENTER HTML BODY HERE</body>
        """
        # e.g., f'<body>event["body"]</body>'

    def gen_text_body(self):
        ''' Compose the text body piece of the email
        '''
        self.BODY_TEXT = """\
                Email body as text, here
        """

    def compose_mail(self):
        ''' Create message container, set various details, and attach files
        '''

        # The character encoding for the email.
        CHARSET = "utf-8"

        # Create a new SES resource and specify a region.
        AWS_REGION = 'us-east-1'
        self.mail_client = boto3.client('ses', region_name=AWS_REGION)

        # Create an instance of multipart/mixed parent container.
        self.msg = MIMEMultipart('mixed')

        # Add subject, from and to lines.
        self.msg['Subject'] = self.SUBJECT
        self.msg['From'] = self.SENDER
        self.msg['To'] = self.RECIPIENT

        # Create a multipart/alternative child container.
        self.msg_body = MIMEMultipart('alternative')

        # Encode the text and HTML content and set the character encoding. This step is
        # necessary if you're sending a message with characters outside the ASCII range.
        textpart = MIMEText(self.BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
        htmlpart = MIMEText(self.BODY_HTML.encode(CHARSET), 'html', CHARSET)

        # Add the text and HTML parts to the child container.
        self.msg_body.attach(textpart)
        self.msg_body.attach(htmlpart)

        self.msg.attach(self.msg_body)

    def generator_wrapper(self):
        ''' Convenience function to call all of the needed functions to generate the email
        '''
        self.set_sender_receiver_subject()
        self.set_titles_block()
        self.gen_html_body()
        self.gen_text_body()
        self.download_files()
        self.compose_mail()
        self.attach_files()

    def send_email(self):
        ''' Send the compiled email
        '''

        try:
            #Provide the contents of the email.
            self.response = self.mail_client.send_raw_email(
                Source=self.SENDER,
                Destinations=[
                    self.RECIPIENT
                ],
                RawMessage={
                    'Data':self.msg.as_string(),
                },
                ConfigurationSetName=self.CONFIGURATION_SET
            )

        except Exception as e:
            print("Error sending email")
            print(e)
            traceback.print_exc()
            sys.exit(1)



