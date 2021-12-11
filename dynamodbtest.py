import boto3
from boto3.dynamodb.conditions import Attr

# Step 0 Init

table = boto3.resource("dynamodb").Table("capacity")

# Step 1 Read the current item
item = table.get_item(Key={"event": int("0")})['Item']
current_version = item["Version"]

# Step 2 Apply transaction
item["Capacity"] = item["Capacity"] - 1
    
# Step 3 Write

# 3.1 Increase the version number so other workers know something changed
item["Version"] += 1

# 3.2 Try to write the item, but only if it hasn't been updated in the mean time
try:
    table.put_item(
        Item=item,
        ConditionExpression=Attr("Version").eq(current_version)
    )
except ClientError as err:
    if err.response["Error"]["Code"] == 'ConditionalCheckFailedException':
        # Somebody changed the item in the db while we were changing it!
        raise ValueError("Balance updated since read, retry!") from err
    else:
        raise err