from fpdf import FPDF  # fpdf class
import boto3
import botocore
from botocore.exceptions import NoCredentialsError

with open('C:\\Users\\Pablo\\.aws\\credentials') as f:
    lines = f.readlines()

ACCESS_KEY = str(lines[1].split("=")[1]).strip()
SECRET_KEY = str(lines[2].split("=")[1]).strip()
TOKEN_KEY  = str(lines[3].split("=")[1]).strip()


pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(40, 10, 'Ticket para concierto de A$AP REOCKY')
pdf.output('ticket1.pdf', 'F')


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def download_from_aws(BUCKET_NAME, KEY):
    
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY)

    try:
        aux = s3.download_file(BUCKET_NAME,KEY,'examples')
        print(aux)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

print("Would You Like to : 1) Upload File 2) Download File 3:) Exit Program ?")

store = input()
    ####################################SEND A MESSAGE##############################################
if int(store) == 1:
    uploaded = upload_to_aws('ticket1.pdf', 'ticketbucket.ta', 'ticket-pdf')


if int(store) == 2:
    download = download_from_aws('amazon-reviews-ml','examples')

else:
    exit()


