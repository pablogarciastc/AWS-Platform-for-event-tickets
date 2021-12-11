import boto3
import time
import paramiko
from scp import SCPClient, SCPException


with open('C:\\Users\\Pablo\\.aws\\credentials') as f:
    lines = f.readlines()
ACCESS_KEY = str(lines[1].split("=")[1]).strip()
SECRET_KEY = str(lines[2].split("=")[1]).strip()
TOKEN_KEY = str(lines[3].split("=")[1]).strip()

accthttp = 'https://sqs.us-east-1.amazonaws.com/644304250224/'

sqs_resource = boto3.resource('sqs', region_name='us-east-1',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    aws_session_token=TOKEN_KEY)

sqs_client = boto3.client('sqs', region_name='us-east-1',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    aws_session_token=TOKEN_KEY)

s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY)

s3_resource = boto3.resource('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY)

ddb_resource = boto3.resource('dynamodb', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY)

ddb_client = boto3.client('dynamodb', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY)

ec2_client = boto3.client(
    'ec2',aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY,
                      aws_session_token=TOKEN_KEY
)


def crear_bucket():
    print("Creando bucket...")
    s3_client.create_bucket(Bucket='ticketbucket.ta')

def crear_colas():
    print("Creando colas...")
    sqs_resource.create_queue(QueueName='inbox', Attributes={'VisibilityTimeout':'10','MessageRetentionPeriod':'14400'})
    sqs_resource.create_queue(QueueName='outbox', Attributes={'VisibilityTimeout':'10','MessageRetentionPeriod':'14400'})


def crear_tablas():
    print("Creando tablas...")
    ddb_resource.create_table(
            TableName='users',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'  # Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    ddb_resource.create_table(
            TableName='capacity',
            KeySchema=[
                {
                    'AttributeName': 'event',
                    'KeyType': 'HASH'  # Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'event',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    time.sleep(8)

    ddb_client.put_item( TableName='users',
        Item={'username':{'S':'test1'},'pass':{'S':'123'}})
    ddb_client.put_item( TableName='users',
        Item={'username':{'S':'test2'},'pass':{'S':'123'}})
    ddb_client.put_item( TableName='users',
        Item={'username':{'S':'test3'},'pass':{'S':'123'}})
    ddb_client.put_item( TableName='users',
        Item={'username':{'S':'test4'},'pass':{'S':'123'}})

    ddb_client.put_item( TableName='capacity',
        Item={'event':{'N':'0'},'Capacity':{'N':'250'},'Version':{'N':'0'}})
    ddb_client.put_item( TableName='capacity',
        Item={'event':{'N':'1'},'Capacity':{'N':'223'},'Version':{'N':'0'}})
    
    autoscaling_client = boto3.client('application-autoscaling')
    #Read capacity
    autoscaling_client.register_scalable_target(ServiceNamespace='dynamodb',
                                            ResourceId='table/capacity',
                                            ScalableDimension='dynamodb:table:ReadCapacityUnits',
                                            MinCapacity=5,
                                            MaxCapacity=10)
    autoscaling_client.register_scalable_target(ServiceNamespace='dynamodb',
                                            ResourceId='table/capacity',
                                            ScalableDimension='dynamodb:table:ReadCapacityUnits',
                                            MinCapacity=5,
                                            MaxCapacity=10)
    #Write capacity
    autoscaling_client.register_scalable_target(ServiceNamespace='dynamodb',
                                            ResourceId='table/users',
                                            ScalableDimension='dynamodb:table:WriteCapacityUnits',
                                            MinCapacity=5,
                                            MaxCapacity=10)
                        
    autoscaling_client.register_scalable_target(ServiceNamespace='dynamodb',
                                            ResourceId='table/users',
                                            ScalableDimension='dynamodb:table:ReadCapacityUnits',
                                            MinCapacity=5,
                                            MaxCapacity=10)
    time.sleep(40)
    activar_servicios()
    

def reiniciar_instancias():
    print("Reiniciando instancias...")
    ec2_client.reboot_instances(
        InstanceIds=[
            "i-08386ebd5ebdc31be",
            "i-0fc42000a359a709b",
            "i-019b4e4e0bf71e6b3",
        ],
    )
  

def activar_servicios():
    print("Activando servicios...")
    k = paramiko.RSAKey.from_private_key_file("C:\\Users\\Pablo\\OneDrive\\Escritorio\\Master\\TA\\Práctica\\P1\\labsuser.pem")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname='ec2-44-194-228-36.compute-1.amazonaws.com', username="ec2-user", pkey=k, allow_agent=False, look_for_keys=False) 
    sftp = c.open_sftp() 
    sftp.put('C:\\Users\\Pablo\\.aws\\credentials', '/home/ec2-user/.aws/credentials')
    sftp.close()
    c.exec_command("python3 backend.py")
    c.close()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname='ec2-3-227-162-108.compute-1.amazonaws.com', username="ec2-user", pkey=k, allow_agent=False, look_for_keys=False) 
    sftp = c.open_sftp() 
    sftp.put('C:\\Users\\Pablo\\.aws\\credentials', '/home/ec2-user/.aws/credentials')
    sftp.close()
    c.exec_command("python3 backend.py")
    c.close()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname='ec2-3-220-51-108.compute-1.amazonaws.com', username="ec2-user", pkey=k, allow_agent=False, look_for_keys=False) 
    sftp = c.open_sftp() 
    sftp.put('C:\\Users\\Pablo\\.aws\\credentials', '/home/ec2-user/.aws/credentials')
    sftp.close()
    stdin, stdout, stderr = c.exec_command("python3 app.py",timeout=10)
    stdin.close()
    try: 
        for line in stdout.read().splitlines():
                print(line)
    except:
        print("Timeout")
    c.close()



def eliminar_bucket():
    print("Eliminando bucket...")
    bucket = s3_resource.Bucket('ticketbucket.ta')
    bucket.objects.all().delete()
    bucket.delete()

def eliminar_colas():
    print("Eliminando colas...")
    sqs_client.delete_queue(QueueUrl=accthttp+'inbox')
    sqs_client.delete_queue(QueueUrl=accthttp+'outbox')


def eliminar_tablas():
    print("Eliminando tablas...")
    table = ddb_resource.Table('capacity')
    table.delete()
    table = ddb_resource.Table('users')
    table.delete()

def inicializar():
    reiniciar_instancias()
    crear_bucket()
    crear_colas()
    crear_tablas()


def eliminar():
    eliminar_colas()2
    eliminar_bucket()
    eliminar_tablas()


def main():
    print("Escriba: \n1 Inicializar \n2 Eliminar")
    store = input()
    if int(store) == 1:
        inicializar()
    elif int(store) == 2:
        eliminar()
    else:
        main()

if __name__ == '__main__':
    main()

