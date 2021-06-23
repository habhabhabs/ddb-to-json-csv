import boto3
import time
from dynamodb_json import json_util as ddbjson
import pandas as pd
import json
import csv

tableName = "mytt-dev-purchaseOrder"
currentTime = str(round(time.time()))

def main():
    dynamodb = boto3.client('dynamodb')

    response = dynamodb.scan(
        TableName = tableName,
        Select = 'ALL_ATTRIBUTES')

    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = dynamodb.scan(
            TableName = tableName,
            Select = 'ALL_ATTRIBUTES',
            ExclusiveStartKey = response['LastEvaluatedKey'])

        data.extend(response['Items'])

    # save your data as csv here
    return data;

if __name__ == "__main__":
    data = main()

    python_data = ddbjson.loads(data)

    # write to json
    with open(('json/output-' + tableName + '-' + currentTime + '.json'), 'w') as f:
        json.dump(python_data, f, ensure_ascii=False, indent=4)


    # write to csv
    data_file = open(('csv/output-' + tableName + '-' + currentTime + '.csv'), 'w')
    csv_writer = csv.writer(data_file)
    count = 0

    for item in python_data:
        if count == 0:
            header = item.keys()
            csv_writer.writerow(header)
            count += 1

        csv_writer.writerow(item.values())

        print("Item: " + str(item))
        print
    
    data_file.close()