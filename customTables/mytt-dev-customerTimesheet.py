import boto3
import time
import datetime
from dynamodb_json import json_util as ddbjson
from collections import OrderedDict
import json
import csv
import sys
import copy
import os

# configuration is made on aws cli

if (len(sys.argv) >= 2 and str(sys.argv[1]) == '--iso'):
    # ISO
    currentTime = datetime.datetime.now().isoformat()
else:
    # epoch
    currentTime = str(round(time.time()))

if (len(sys.argv) == 2 and str(sys.argv[1]) == '--iso') or (len(sys.argv) == 1):
    tableName = "mytt-uat-customerTimesheet" # change here to indicate default table
elif (len(sys.argv) == 1 or len(sys.argv) == 2):
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

    if not os.path.exists('../json/'):
        os.makedirs('../json/', exist_ok=True)
    if not os.path.exists('../csv/'):
        os.makedirs('../csv/', exist_ok=True)

    python_data = ddbjson.loads(data)

    internal_timesheet_record_data_file = open(('../csv/output-' + tableName + '-internal-record-' + currentTime + '.csv'), 'w')
    internal_timesheet_record_csv_writer = csv.writer(internal_timesheet_record_data_file)

    internal_timesheet_data_file = open(('../csv/output-' + tableName + '-internal-' + currentTime + '.csv'), 'w')
    internal_timesheet_csv_writer = csv.writer(internal_timesheet_data_file)

    itemCount = 0
    recordItemCount = 0
    for item in python_data:
        itemDup = copy.copy(item) # dereference item pointer by copying item to memory (duplicate)
        # fetch details of the particular timesheet (all parent items)
        itemDup["dailyRecord"] = "refer to internal-record"
        
        # check for possible broken records
        if not 'supervisorApprovalName' in itemDup:
            itemDup["supervisorApprovalName"] = ""
        if not 'supervisorApprovalEmployeeNo' in itemDup:
            itemDup["supervisorApprovalEmployeeNo"] = ""
        if not 'supervisorApprovalId' in itemDup:
            itemDup["supervisorApprovalId"] = ""
        if not 'customerApprovalId' in itemDup:
            itemDup["customerApprovalId"] = ""
        if not 'customerApprovalName' in itemDup:
            itemDup["customerApprovalName"] = ""
        itemDup = json.dumps(itemDup, sort_keys=True) # convert unsorted json object to sorted json string
        itemDup = json.loads(itemDup) # convert back json string to json object
        
        if itemCount == 0:
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

    print(sys.argv)
    print(len(sys.argv))