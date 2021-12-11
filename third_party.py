import boto3
import threading
import time
from fpdf import FPDF  # fpdf class

with open('C:\\Users\\Pablo\\.aws\\credentials') as f:
    lines = f.readlines()
ACCESS_KEY = str(lines[1].split("=")[1]).strip()
SECRET_KEY = str(lines[2].split("=")[1]).strip()
TOKEN_KEY = str(lines[3].split("=")[1]).strip()
bucket_name = "ticketbucket.ta"
event_names = ["Celta-Depor", "Concierto de Fleetwood Mac"]
accthttp = 'https://sqs.us-east-1.amazonaws.com/644304250224/'
client = boto3.resource('sqs', region_name='us-east-1',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    aws_session_token=TOKEN_KEY)


class Listener(object):
    def __init__(self):
        self.stuff = 'Listening loop'

    def listen(self):
        global downloaded
        global nickname
        while True:
            url = accthttp + str("outbox")
            receipt = client.Queue(url=url).receive_messages()
            # print(receipt)
            if (receipt):
                for message in receipt:
                    # si es del usuario correcto se coge
                    if (message.body.split("#")[1] == nickname):
                        message.delete(
                                    QueueUrl=url, ReceiptHandle=message.receipt_handle)
                        if(message.body != ""):
                            filename = str(message.body.split("#")[0])
                            print("La clave que necesitas para descargar tu entrada es: " + filename)
                            downloaded = 1
                        else:
                            print("Se excedía el número de entradas.")
                    else: #si no se devuelve a la cola
                        message.change_visibility(QueueUrl=url, ReceiptHandle=message.receipt_handle, VisibilityTimeout=0)
                    
            
def download_from_aws(BUCKET_NAME, KEY):
    
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY)

    try:
        s3.download_file(BUCKET_NAME,KEY,KEY)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("La entrada introduce no existe.")
        else:
            raise

def main_function():
    global nickname
    global downloaded
    downloaded = 1
    noId = 0
    print("Primero deberá logearse")
    while(noId  == 0):
        print("Introduzca su nickname:")
        nickname = input()
        print("Introduzca su contraseña:")
        password = input()
        table = boto3.resource("dynamodb").Table("users")
        try:
            item = table.get_item(Key={"username": nickname})['Item']
            passw = item["pass"]
            if passw == password:
                noId = 1
        except:
           print("No existe")
      

    while True:    
        if(downloaded == 1):
            print("Bienvenido al servicio de eventos, introduzca 1 para comprar entradas o 2 para descargarlas")
            store = input()
            if(int(store) == 1):
                print("A continuación los eventos disponibles")
                for x in range(0,len(event_names)):
                    print(str(x) + "." + " " + event_names[x])
                print("Porfavor seleccione el número del evento o presione " + str(len(event_names)) + " para salir" )
                evento = input()
                if(int(evento) is len(event_names)):
                    exit()
                else:
                    print("Por favor introduzca el número de entradas que quiere (Máximo 6)")
                    n_tickets = input()
                    if(int(n_tickets) < 7 ):
                        url = accthttp+str("inbox")
                        client.Queue(url=url).send_message(
                                MessageBody=evento+"-"+n_tickets + "-" + nickname)
                        print("Esperando por la clave")
                        downloaded = 0
                    else:
                        print("Excediste el número máximo de entradas permitido.")
            if(int(store)==2):
                print("Introduzca la clave de su entrada")
                store2 = input()
                download_from_aws(bucket_name, store2)
                print("La entrada fue descargada.")


            


def main():
    a = Listener()
    t1 = threading.Thread(target=a.listen)
    t1.setDaemon(True)
    t1.start()
    main_function()

if __name__ == '__main__':
    main()
