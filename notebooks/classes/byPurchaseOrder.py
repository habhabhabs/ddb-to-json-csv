import boto3
from dynamodb_json import json_util as ddbjson
import json
import copy
import pandas as pd
from json2table import convert

# configuration is made on aws cli

def __fetchDb(tableName):       
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
    return data

def getAllPublicHolidays():
    data = __fetchDb('mytt-uat-publicHoliday')

    python_data = ddbjson.loads(data)

    dataframe = pd.DataFrame.from_dict(python_data)
    print(dataframe)

    # for item in python_data:
    #     # fetch details of the particular timesheet (all parent items)
    #     itemDup = copy.copy(item)  # dereference item pointer by copying item to memory (duplicate)
    #     # itemDup["dailyRecord"] = "refer to internal-record"

    #     # # check for possible broken records
    #     # if not 'supervisorApprovalName' in itemDup:
    #     #     itemDup["supervisorApprovalName"] = ""
    #     # if not 'supervisorApprovalEmployeeNo' in itemDup:
    #     #     itemDup["supervisorApprovalEmployeeNo"] = ""
    #     # if not 'supervisorApprovalId' in itemDup:
    #     #     itemDup["supervisorApprovalId"] = ""
    #     itemDup = json.dumps(itemDup, sort_keys=True) # convert unsorted json object to sorted json string
    #     itemDup = json.loads(itemDup) # convert back json string to json object

    #     dataframe = pd.DataFrame.from_dict(itemDup)
    #     print(dataframe)