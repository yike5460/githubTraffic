## continuous collecting github traffic metrics with AWS serverless arch

This project is a sample project to show how to use AWS CDK to deploy a lambda function to periodically collect GitHub traffic data and store it in AWS DynamoDB, without the limitation of 14 days data retention in GitHub. Currently it only supports collecting traffic data for public repositories within awslabs, you can customize the code to collect data for other repositories.

The arch is quite simple and straight forward, using eventbridge cron job to periodically (14 days) trigger lambda to fetch github traffic metric using official api, then store all the data into dynamodb with schema like pk:type, sk:timestamp.

Just install AWS CDK and run the following command to deploy the project to your AWS account, it will deploy 2 dynamoDB tables with fixed table name ('stable-diffusion-aws-extension', 'aws-cloudfront-extensions' and 'aws-ai-solution-kit'), the repoNameList parameter is a comma separated list of repo names and should match the 2 dynamoDB table name.
```
cdk deploy --parameters accessToken='<your github access token>' --parameters repoNameList='<repo within awslabs>'
```

After such CloudFormation succesful installed in your account, you can check periodically to check the data in database with command below (AWS CLI required)

```
# filter items with type value = "views" and display only timestamp, uniques and view items with sorted timestamp and transform to json format and export to json file
aws dynamodb scan --table-name aws-cloudfront-extensions --region us-east-1 | jq -r '.Items[] | select(.type.S == "views") | {timestamp: .timestamp.S, uniques: .uniques.N, views: .views.N}' | jq -s 'sort_by(.timestamp)' | jq -s '.' > views.json
```

Then you can use online json plot tool or diagram.py in repo to do the data visualization.
```
python diagram.py
```

![GitHubTraffic](./GitHubTraffic.png)
