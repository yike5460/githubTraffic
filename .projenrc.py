from projen.awscdk import AwsCdkPythonApp

project = AwsCdkPythonApp(
    author_email="yike5460@163.com",
    author_name="yike5460",
    cdk_version="2.1.0",
    module_name="githubTraffic",
    name="githubTraffic",
    version="0.1.0",
)

project.synth()