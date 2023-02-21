import os
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_kms as _kms,
    aws_dynamodb as _dynamodb
)

absolute_path = os.path.dirname(__file__)
demo_app_src_folder = os.path.join(absolute_path, 'src/lambda')

PROJECT_NAME = "demo_application"

class DemoApplicationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, project_name=PROJECT_NAME, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.project_name = project_name

        kms_key = self.__create_ecryption_key()
        self.create_app_log_group(project_name, kms_key)
        lambda_role = self.create_lambda_iam_role(
            f"{project_name}-lambda-role", f"{project_name}-lambda-policy", project_name)
        self.create_lambda(f"{project_name}-lambda", lambda_role)
        self.__create_table('Table', f"{project_name}-table")

    def __create_ecryption_key(self) -> _kms.Key:
        """
        Creates KMS key for encryption at rest for CloudWatch Logs

        :returns: Created KMS Key
        :rtype: kms.Key
        """
        alias=f"{self.project_name}-encryption-key"

        key = _kms.Key(
            self, "ProjectEncryptionKey",
            removal_policy=RemovalPolicy.DESTROY,
            enable_key_rotation=True,
            pending_window=Duration.days(7),
            alias=alias,
            description=f"KMS key for encrypting all data related to {self.project_name} in the account.",
            policy=_iam.PolicyDocument(
                statements=[
                    # Base root access
                    _iam.PolicyStatement(
                        sid="Root Admin access", effect=_iam.Effect.ALLOW,
                        principals=[_iam.AccountRootPrincipal()],
                        actions=["kms:*"],
                        resources=["*"]
                    ),
                    # Allows the key to be used to encrypt/decrypt CloudWatch Logs/Log Groups
                    _iam.PolicyStatement(
                        sid='Log Group Encryption', effect=_iam.Effect.ALLOW,
                        principals=[_iam.ServicePrincipal(
                            f"logs.{self.region}.amazonaws.com")],
                        actions=[
                            "kms:DescribeKey",
                            "kms:DescribeCustomKeyStores",
                            "kms:Decrypt",
                            "kms:Encrypt",
                            "kms:GenerateDataKey",
                            "kms:GenerateDataKeyWithoutPlaintext",
                            "kms:GenerateDataKeyPairWithoutPlaintext",
                            "kms:GenerateDataKeyPair",
                            "kms:ReEncryptFrom",
                            "kms:ReEncryptTo"
                        ],
                        resources=["*"],
                        conditions={
                            "ArnEquals": {
                                "kms:EncryptionContext:aws:logs:arn": f"arn:aws:logs:{self.region}:{self.account}:*"
                            }
                        }
                    )
                ]
            )
        )

        CfnOutput(self, 'KmsKeyArn', value=key.key_arn,
                  description='ARN of the KMS key used for encryption at rest')

        return key

    def create_app_log_group(self, project_name: str, kms_key: _kms.Key) -> _logs.LogGroup:
        """
        Creates the LogGroup for the application
        """
        return _logs.LogGroup(
            self, 'ApplicationLogGroup', log_group_name=f"/aws/lambda/{project_name}", encryption_key=kms_key, removal_policy=RemovalPolicy.DESTROY
        )

    def create_lambda_iam_role(self, role_name: str, policy_name: str, project_name: str) -> _iam.Role:
        """
        Creates the IAM Role for the Lambda funtion
        """

        policy = _iam.ManagedPolicy(
            self, 'LambdaPolicy', managed_policy_name=policy_name, statements=[
                _iam.PolicyStatement(
                    sid='LambdaLogGroup', effect=_iam.Effect.ALLOW,
                    actions=[
                        'logs:CreateLogGroup',
                        'logs:CreateLogStream',
                        'logs:PutLogEvents'
                    ],
                    resources=[
                        f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/lambda/{project_name}"]
                )
            ]
        )

        return _iam.Role(self, 'ApplicationLambdaRole', role_name=role_name, assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com'), managed_policies=[policy], path='/')

    def create_lambda(self, function_name: str, lambda_role: _iam.Role) -> _lambda.Function:

        list_items_lambda = _lambda.Function(
            self, 'ListItemsHandler',
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(demo_app_src_folder),
            role=lambda_role,
            # tracing=_lambda.Tracing.ACTIVE,
            handler='list_items.handler',
            timeout=Duration.seconds(10),
            retry_attempts=0
        )

        list_items_lambda.node.add_dependency(lambda_role)

        return list_items_lambda
    
    def __create_table(self, name: str, table_name: str) -> _dynamodb.Table:

        return _dynamodb.Table(self, name, table_name=table_name, partition_key=_dynamodb.Attribute(name="id", type=_dynamodb.AttributeType.STRING))
    
    


