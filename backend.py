import boto3
import time
from boto3.dynamodb.conditions import Attr
from fpdf import FPDF  # fpdf class

with open('/home/ec2-user/.aws/credentials') as f:
    lines = f.readlines()

ACCESS_KEY = str(lines[1].split("=")[1]).strip()
SECRET_KEY = str(lines[2].split("=")[1]).strip()
TOKEN_KEY  = str(lines[3].split("=")[1]).strip()
bucket_name = "ticketbucket.ta"
event_list = [{"nombre" : "Celta-Depor",
          "capacidad" : "100", },{'nombre':'Concierto de Fleetwood Mac', "capacidad" : "50",}]


########################################INITIALIZE CONNECTION TO AWS VIA BOTO3 'CLIENT'#############################################
client = boto3.resource('sqs', region_name='us-east-1',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    aws_session_token=TOKEN_KEY)

accthttp='https://sqs.us-east-1.amazonaws.com/644304250224/' #id de sqs

def create_pdf(body):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(40, 10, 'GRACIAS POR UTILIZAR NUESTRO SERVICIO DE EVENTOS.')
    pdf.set_draw_color(255, 0, 0)
    pdf.line(20, 20, 160, 20)
    pdf.set_font('Arial','B', 16)
    pdf.cell(-30,120,str(body)); 
    table = boto3.resource("dynamodb").Table("capacity")
    item = table.get_item(Key={"event": int(event)})['Item']
    capacidad = item["Capacity"]
    file_name = event_list[event]["nombre"].replace(" ", "") + "-" + str(capacidad) + ".pdf"
    if(event == 0):
        pdf.image('celta.png', x=85, y=100, w=40, h=40)
    else:
        pdf.image('fleetwood.png', x=85, y=100, w=40, h=40)

    pdf.output(str(file_name), 'F')
    return file_name

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

def create_pdfs(event,n_tickets):
    pdf_body = "Ticket "
    table = boto3.resource("dynamodb").Table("capacity")
    item = table.get_item(Key={"event": int(event)})['Item']
    capacidad = item["Capacity"]
    for i in range(int(n_tickets)):
        pdf_body = pdf_body + str( int(capacidad) + int(i) ) + ","
    pdf_body = pdf_body[:-1] + " del " + event_list[event]["nombre"]
    pdf_name = create_pdf(pdf_body)
    upload_to_aws(pdf_name, bucket_name, pdf_name)
    url = "https://s3.amazonaws.com/ticketbucket.ta/" + pdf_name
    return pdf_name

def send_key(pdf_name):
    url = accthttp+str("outbox")
    client.Queue(url=url).send_message(
                MessageBody=pdf_name)

def update_dynamo(event, n_tickets):
    table = boto3.resource("dynamodb").Table("capacity")
    try:
        item = table.get_item(Key={"event": int(event)})['Item']
    except:
            return None
    current_version = item["Version"]
    if((item["Capacity"] - int(n_tickets)) < 0 ):
        print("Se devuelve None")
        return "Null"
    else:
        item["Capacity"] = item["Capacity"] - int(n_tickets)
        item["Version"] += 1
        try:
            table.put_item(
                Item=item,
                ConditionExpression=Attr("Version").eq(current_version)
            )
            return "error"
        except ClientError as err:
            if err.response["Error"]["Code"] == 'ConditionalCheckFailedException':
                # Somebody changed the item in the db while we were changing it!
                raise ValueError("Balance updated since read, retry!") from err
            else:
                raise err



while True:
        url = accthttp + str("inbox")
        receipt = client.Queue(url=url).receive_messages()
        #print(receipt)
        if (receipt):
            for message in receipt:
                print(message.body)
                #print(message)
                message.delete(QueueUrl=url, ReceiptHandle=message.receipt_handle)
                event = int(message.body.split("-")[0])
                n_tickets = str(message.body.split("-")[1])
                nickname = str(message.body.split("-")[2])
                aux_var = update_dynamo(event, n_tickets)
                if(aux_var != "Null"):
                    pdf_name = create_pdfs(event,n_tickets)
                    send_key(pdf_name+"#"+nickname)
                else:
                    send_key("Null#"+nickname)
       
           



