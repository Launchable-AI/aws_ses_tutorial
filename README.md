This repo contains code to accompany our tutorial on using AWS Simple Email
Service (SES) with Bubble.io.

The simpler lambda function (in ses_template_simple) contains the sample code
provided in the AWS SES developer guide
(https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-using-sdk-python.html)
with just a few modifications.

The other directory (ses_template_with_attachments), provides a code sample for
sending mails with SES and attaching to them files that are stored in an S3
bucket.  This can be helpful for sending reports, spreadsheets, multimedia, etc.
