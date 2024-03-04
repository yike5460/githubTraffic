import os
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_events as events_
from aws_cdk import aws_events_targets as targets_
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import CfnParameter
from aws_cdk import Duration

class MyStack(Stack):
  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # cdk parameters
    access_token = CfnParameter(self, 'accessToken', description='GitHub access token', type='String')
    # obsolete
    repo_name_list = CfnParameter(self, 'repoNameList', description='GitHub repo name list', type='String')

    # create a lambda function to fetch traffic data of GitHub repositories and store it in a database
    github_traffic = lambda_.DockerImageFunction(
      self, 'githubTraffic',
      code=lambda_.DockerImageCode.from_image_asset('lambda/traffic'),
      timeout = Duration.seconds(300),
    )

    # cron expression to run the lambda function every 14 days
    cron_expression = 'cron(0 0 1/14 * ? *)'

    # create a rule to trigger the lambda function
    rule = events_.Rule(self, 'githubTrafficRule',
                        schedule=events_.Schedule.expression(cron_expression)
                        )
    
    # set the lambda function as a target of the rule
    rule.add_target(targets_.LambdaFunction(github_traffic))

    # create multiple tables to store the traffic data with table name inherited from the parameter
    table = dynamodb.Table(self, 'githubTrafficTableSD',
                            table_name='stable-diffusion-aws-extension',
                            partition_key=dynamodb.Attribute(name='type', type=dynamodb.AttributeType.STRING),
                            sort_key=dynamodb.Attribute(name='timestamp', type=dynamodb.AttributeType.STRING),
                            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
                            )
    # grant the lambda function read/write permissions to the table
    table.grant_read_write_data(github_traffic)

    table = dynamodb.Table(self, 'githubTrafficTableCDN',
                            table_name='aws-cloudfront-extensions',
                            partition_key=dynamodb.Attribute(name='type', type=dynamodb.AttributeType.STRING),
                            sort_key=dynamodb.Attribute(name='timestamp', type=dynamodb.AttributeType.STRING),
                            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
                            )
    # grant the lambda function read/write permissions to the table
    table.grant_read_write_data(github_traffic)

    table = dynamodb.Table(self, 'githubTrafficTableAI',
                            table_name='aws-ai-solution-kit',
                            partition_key=dynamodb.Attribute(name='type', type=dynamodb.AttributeType.STRING),
                            sort_key=dynamodb.Attribute(name='timestamp', type=dynamodb.AttributeType.STRING),
                            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
                            )
    # grant the lambda function read/write permissions to the table
    table.grant_read_write_data(github_traffic)
    
    # set the table name as an environment variable of the lambda function
    github_traffic.add_environment('RepoNameList', repo_name_list.value_as_string)
    github_traffic.add_environment('AccessToken', access_token.value_as_string)
