# Lambda to get GitHub traffic data
# Path: githubTraffic/lambda/main.py
import os
import boto3
import requests
import datetime
import time

# Initialize the DynamoDB client
client = boto3.client('dynamodb')
# get the repo name from the environment variables
repo_name_list = os.environ['RepoNameList']
# get the GitHub access token from the environment variables
access_token = os.environ['AccessToken']

# Define a function to insert traffic data into DynamoDB
def insert_traffic_data(table_name, type, timestamp, repo_name, count, uniques, referrer, path, title):
    # check if redundant data is being inserted judging by the timestamp & type, type includes clones, views, referrers, paths
    try:
        response = client.get_item(
            TableName=str(table_name),
            Key={
                'type': {'S': type},
                'timestamp': {'S': str(timestamp)}
            }
        )
        # remove such redundant data check since we will do such interval job in 14 days
        if 'Item' in response:
            return None
        try:
            response = client.put_item(
                TableName=str(table_name),
                Item={
                    'type': {'S': type},
                    'timestamp': {'S': str(timestamp)},
                    'repo_name': {'S': str(repo_name)},
                    'uniques': {'N': str(uniques)},
                    'count': {'N': str(count)},
                    'referrer': {'S': str(referrer)},
                    'path': {'S': str(path)},
                    'title': {'S': str(title)}
                }
            )
            return None
        except Exception as e:
            print('error: {} happened in put item'.format(e))
    except Exception as e:
        print('error: {} happened in get item'.format(e))

def fetch_traffic_data(table_name, type):
    # fetch all the traffic data of the repo for all time range
    # or use aws cli directly: aws dynamodb scan --table-name <your table name> --region <your region> | jq '.Items[] | {repo_name: .repo_name.S, count: .count.N, timestamp: .timestamp.S}'
    try:
        response = client.scan(
            TableName=str(table_name),
            FilterExpression='type = :type',
            ExpressionAttributeValues={
                ':type': {'S': str(type)}
            }
        )
    except Exception as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return None
    return response

# entry point for the lambda function
def handler(_event, _context):
    for repo_name in repo_name_list.split(','):
        # get the traffic data of the repo, we could use the pyGithub to get the data due to the limitation of Lambda not support multiprocessing.Queue or multiprocessing.Pool
        repo_name = repo_name.strip()
        response = requests.get('https://api.github.com/repos/awslabs/' + repo_name + '/traffic/views', headers={'Authorization': 'Bearer ' + access_token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})

        # get the total count of views check if views data is available
        if 'views' not in response.json():
            print('views data not available')
            continue

        for i in range(0, len(response.json()['views'])):
            timestamp = response.json()['views'][i]['timestamp']
            count = response.json()['views'][i]['count']
            uniques = response.json()['views'][i]['uniques']
            # sleep 1s to allow different timestamp
            time.sleep(1)
            insert_traffic_data(repo_name, 'views', timestamp, repo_name, count, uniques, None, None, None)

        # get the clone data of the repo
        response = requests.get('https://api.github.com/repos/awslabs/' + repo_name + '/traffic/clones', headers={'Authorization': 'Bearer ' + access_token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})

        # get the total count of clones check if clones data is available
        if 'clones' not in response.json():
            print('clones data not available')
            continue

        for i in range(0, len(response.json()['clones'])):
            timestamp = response.json()['clones'][i]['timestamp']
            count = response.json()['clones'][i]['count']
            uniques = response.json()['clones'][i]['uniques']
            # sleep 1s to allow different timestamp
            time.sleep(1)
            insert_traffic_data(repo_name, 'clones', timestamp, repo_name, count, uniques, None, None, None)

        # get the Referring sites data of the repo
        response = requests.get('https://api.github.com/repos/awslabs/' + repo_name + '/traffic/popular/referrers', headers={'Authorization': 'Bearer ' + access_token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})

        # get the total count of Referring sites check if Referring sites data is available
        if 'referrer' in response.json()[0].keys():
            for i in range(0, len(response.json())):
                # generate current UTC timestamp, e.g。 2023-03-01T00:00:00Z
                timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                count = response.json()[i]['count']
                uniques = response.json()[i]['uniques']
                referrer = response.json()[i]['referrer']
                 # sleep 1s to allow different timestamp
                time.sleep(1)
                insert_traffic_data(repo_name, 'referrer', timestamp, repo_name, count, uniques, referrer, None, None)

        # get the Popular content data of the repo
        response = requests.get('https://api.github.com/repos/awslabs/' + repo_name + '/traffic/popular/paths', headers={'Authorization': 'Bearer ' + access_token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})

        # get the total count of Popular content check if Popular content data is available
        if 'path' in response.json()[0].keys():
            for i in range(0, len(response.json())):
                # generate current UTC timestamp, e.g。 2023-03-01T00:00:00Z
                timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                count = response.json()[i]['count']
                uniques = response.json()[i]['uniques']
                path = response.json()[i]['path']
                title = response.json()[i]['title']
                 # sleep 1s to allow different timestamp
                time.sleep(1)
                insert_traffic_data(repo_name, 'path', timestamp, repo_name, count, uniques, None, path, title)


            
            
