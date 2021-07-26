import boto3
import time
from dynamodb_json import json_util as ddbjson
import json
import csv
import sys
import pandas as pd
import os

# configuration is made on aws cli

if (len(sys.argv) >= 2 and str(sys.argv[1]) == '--iso'):
    # ISO
    currentTime = datetime.datetime.now().isoformat()
else:
    # epoch
    currentTime = str(round(time.time()))

if (len(sys.argv) == 2 and str(sys.argv[1]) == '--iso'):
    tableName = "mytt-uat-publicHoliday" # change here to indicate default table
elif (len(sys.argv) == 2):
    tableName = str(sys.argv[1])
elif (len(sys.argv) == 3):
    tableName = str(sys.argv[2])
else:
    print("Error! Argument invalid")
    exit()

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

    if not os.path.exists('json/'):
        os.makedirs('json/', exist_ok=True)
    if not os.path.exists('csv/'):
        os.makedirs('csv/', exist_ok=True)

    python_data = ddbjson.loads(data)

    # write to json
    with open(('json/output-' + tableName + '-' + currentTime + '.json'), 'w') as f:
        json.dump(python_data, f, ensure_ascii=False, indent=4)

    # write to csv
    data_file = open(('csv/output-' + tableName + '-' + currentTime + '.csv'), 'w')
    csv_writer = csv.writer(data_file)
    count = 0

    for item in python_data:
        if count == 0: # write header if first row
            header = item.keys()
            csv_writer.writerow(header)
            count += 1

        csv_writer.writerow(item.values())

        # print every record
        print("Item: " + str(item))
        print
    
    data_file.close()