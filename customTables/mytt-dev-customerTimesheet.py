import boto3
import time
from dynamodb_json import json_util as ddbjson
import json
import csv
import sys
import copy
import pandas as pd

# configuration is made on aws cli

if (len(sys.argv) == 1):
    tableName = "mytt-dev-customerTimesheet" # change here to indicate default table
else:
    tableName = str(sys.argv[1])

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

    internal_timesheet_record_data_file = open(('../csv/output-' + tableName + '-internal-record-' + currentTime + '.csv'), 'w')
    internal_timesheet_record_csv_writer = csv.writer(internal_timesheet_record_data_file)

    internal_timesheet_data_file = open(('../csv/output-' + tableName + '-internal-' + currentTime + '.csv'), 'w')
    internal_timesheet_csv_writer = csv.writer(internal_timesheet_data_file)

    itemCount = 0
    recordItemCount = 0
    for item in python_data:
        # fetch details of the particular timesheet (all parent items)
        itemDup = json.dumps(copy.copy(item), sort_keys=True)  # to prevent overwriting original json object (copy value not reference)
        itemDup["dailyRecord"] = "refer to internal-record"
        # check for possible broken records
        if not 'supervisorApprovalName' in itemDup:
            itemDup["supervisorApprovalName"] = ""
        if not 'supervisorApprovalEmployeeNo' in itemDup:
            itemDup["supervisorApprovalEmployeeNo"] = ""
        if not 'supervisorApprovalId' in itemDup:
            itemDup["supervisorApprovalId"] = ""

        
        
        # if itemCount == 0:
        header = itemDup
        internal_timesheet_csv_writer.writerow(header)
        internal_timesheet_csv_writer.writerow(itemDup.values())
        itemCount += 1

        # fetch all day records in all timesheets (all child items)
        if (item["dailyRecord"] != None):
            for itemDR in item["dailyRecord"]:
                itemDR["reportMonth"] = item["reportMonth"]                
                if recordItemCount < 1:
                    header = itemDR
                    internal_timesheet_record_csv_writer.writerow(header)
                # itemDR["startTime"] = itemDR["startTime"].strftime("%Y-%m-%d")
                # itemDR["endTime"] = itemDR["endTime"].strftime("%Y-%m-%d")
                # itemDR["day"] = itemDR["day"].strftime("%Y-%m-%d")
                
                internal_timesheet_record_csv_writer.writerow(itemDR.values())
                recordItemCount += 1
                print("Item: " + str(item["dailyRecord"]))

    # # write to json
    # with open(('json/output-' + tableName + '-' + currentTime + '.json'), 'w') as f:
    #     json.dump(python_data, f, ensure_ascii=False, indent=4)

    # # write to csv
    # data_file = open(('csv/output-' + tableName + '-' + currentTime + '.csv'), 'w')
    # csv_writer = csv.writer(data_file)
    # count = 0

    # for item in python_data:
    #     if count == 0: # write header if first row
    #         header = item.keys()
    #         csv_writer.writerow(header)
    #         count += 1

    #     csv_writer.writerow(item.values())

    #     # print every record
    #     print("Item: " + str(item))
    #     print
    
    # data_file.close()
    internal_timesheet_data_file.close()
    internal_timesheet_record_data_file.close()