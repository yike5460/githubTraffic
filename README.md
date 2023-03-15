

This project is a sample project to show how to use AWS CDK to deploy a lambda function to periodically collect GitHub traffic data and store it in AWS DynamoDB, without the limitation of 14 days data retention in GitHub. Currently it only supports collecting traffic data for public repositories within awslabs, you can customize the code to collect data for other repositories.

Just install AWS CDK and run the following command to deploy the project to your AWS account, it will deploy 2 dynamoDB tables with fixed table name ('aws-cloudfront-extensions' and 'aws-ai-solution-kit'), the repoNameList parameter is a comma separated list of repo names and should match the 2 dynamoDB table name.
```
cdk deploy --parameters accessToken='<your github access token>' --parameters repoNameList='<repo within awslabs>'
```
