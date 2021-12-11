import boto3
from fpdf import FPDF  # fpdf class



with open('C:\\Users\\Pablo\\.aws\\credentials') as f:
    lines = f.readlines()

ACCESS_KEY = str(lines[1].split("=")[1]).strip()
SECRET_KEY = str(lines[2].split("=")[1]).strip()
TOKEN_KEY  = str(lines[3].split("=")[1]).strip()

########################################INITIALIZE CONNECTION TO AWS VIA BOTO3 'CLIENT'#############################################
client = boto3.resource('sqs', region_name='us-east-1',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    aws_session_token=TOKEN_KEY)

accthttp='https://sqs.us-east-1.amazonaws.com/644304250224/'

###INPUT THE IAM CREDENTIALS WITH PERMISSIONS TO THE AWS ACCOUNT AND RESOURCE YOU'RE TRYING TO ACCESS.


print("##########################################")
print("AVAILABLE QUEUES : URLS")

#The response is NOT a resource, but gives you a message ID and MD5
for queue in client.queues.all():
    print(queue.url)
#
print("##########################################")
while True:



    print("Would You Like to : 1) Send a Message 2) Receive a Message 3:) Exit Program ?")
    store = input()
    ####################################SEND A MESSAGE##############################################
    if int(store) == 1:
        print("Please Input the NAME of the QUEUE to send a message to:")
        store2 = input()
        url = accthttp+str(store2)
        print("Please Input the Message")
        store3 = input()
        client.Queue(url=url).send_message(
            MessageBody=store3)
     ###############################################################################################
    #####################################READ AND DELETE MESSAGES###################################
    if int(store) == 2:
        print("Please Input the NAME of the QUEUE read a message from:")
        store2 = input()
        url = accthttp + str(store2)
        print(url)
        # receipt = client.Queue(url=url).receive_messages()
        # receipt1 = client.Queue(url=url).receive_messages()
        while True:
            print("Would You Like to Try the Queue? (1 or 2)")
            if int(input())== 1:

                receipt = client.Queue(url=url).receive_messages()

        # print(receipt)
                for message in receipt:
                    print(message.body)
                    print(message)
                    message.delete(QueueUrl=url, ReceiptHandle=message.receipt_handle)
                    print("this message has been deleted.")

            else:
                print("have a nice day!")
                break