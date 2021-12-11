
from flask import Flask, Response, render_template, request, url_for, flash, redirect
import sys
import boto3
import threading
import time
from fpdf import FPDF  # fpdf class


with open('/home/ec2-user/.aws/credentials') as f:
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
app = Flask(__name__)


class Listener(object):
    def __init__(self):
        self.stuff = 'Listening loop'

    def listen(self):
        global downloaded
        while True:
            url = accthttp + str("outbox")
            receipt = client.Queue(url=url).receive_messages()
            # print(receipt)
            if (receipt):
                for message in receipt:
                    # print(message.body)
                    message.delete(
                        QueueUrl=url, ReceiptHandle=message.receipt_handle)
                    if(message.body != ""):
                        filename = str(message.body)
                        print(
                            "La clave que necesitas para descargar tu entrada es: " + filename.split("-")[0])
                        downloaded = 1
                    else:
                        print("Se excedía el número de entradas.")


def download_from_aws(bucket_name, clave):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY)

    file = s3.get_object(Bucket=bucket_name, Key=clave)
    response = Response(
        file['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename=" + clave}
    )
    return response


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        table = boto3.resource("dynamodb").Table("users")
        try:
            item = table.get_item(Key={"username": name})['Item']
        except:
            return render_template('login.html')
        passw = item["pass"]
        if passw == password:
            nombre = request.form['name']
            try:
                return redirect(url_for('entradas', name=nombre))
            except:
                print("Oops!", sys.exc_info()[0], "occurred.")
    else:
        return render_template('login.html')


@app.route('/entradas', methods=['GET', 'POST'])
def entradas():
    global downloaded
    nickname = request.args.get('name')
    downloaded = 1
    if request.method == 'POST':
        if "entrada" in request.form and "event" in request.form:
            entrada = request.form['entrada']
            event = request.form['event']
            if(entrada != "" and event != ""):
                if int(entrada) > 6:
                    flash('Bad Request!')
                    return render_template('home.html')
                print("Se pidieron " + entrada + " del evento " + event)
                url = accthttp+str("inbox")
                client.Queue(url=url).send_message(
                    MessageBody=event+"-"+entrada + "-" + nickname)
                print("Esperando por la clave")
                downloaded = 0
                while(downloaded == 0):
                    url = accthttp + str("outbox")
                    receipt = client.Queue(url=url).receive_messages()
                    if (receipt):
                        for message in receipt:
                            print(message.body)
                            # si es del usuario correcto se coge
                            if (message.body.split("#")[1] == nickname):
                                message.delete(
                                    QueueUrl=url, ReceiptHandle=message.receipt_handle)
                                if(message.body != ""):
                                    filename = str(message.body.split("#")[0])
                                    downloaded = 1
                                else:
                                    print("Se excedía el número de entradas.")
                            else:  # si no se devuelve a la cola
                                message.change_visibility(
                                    QueueUrl=url, ReceiptHandle=message.receipt_handle, VisibilityTimeout=0)

                return render_template('home.html', value="La clave del pdf es: " + filename.split("#")[0])
        if "clave" in request.form:
            clave = request.form['clave']
            if(clave != ""):
                response = download_from_aws(bucket_name, clave)
                return response
    return render_template('home.html')


if __name__ == "__main__":
    app.secret_key = 'zse4rfvbgy6YHnj8IKMko0pl'
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=False)
