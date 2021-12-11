from sqs_listener import SqsListener
import os
os.environ["AWS_ACCOUNT_ID"] = "644304250224"


class MyListener(SqsListener):
    def handle_message(self, body, attributes, messages_attributes):
        run_my_function(body['param1'], body['param2'])

listener = MyListener('queue1', region_name='us-east-1')
listener.listen()