from constructs import Construct
from aws_cdk import (
    aws_cloudwatch as _cloudwatch,
    aws_lambda as _lamda,
    aws_dynamodb as _dynamoDB
)

class SmartDashboard(Construct):

    def __init__(self, scope: Construct, id: str, application_name: str) -> None:
        super().__init__(scope, id)

        dashboard = _cloudwatch.Dashboard(
            self, f"{application_name}-Dashboard")

        for element in scope.node.children:

            if isinstance(element, _lamda.Function):
                dashboard.add_widgets(
                    _cloudwatch.SingleValueWidget(
                        title=f"{element.function_name} Duration (AVG, Max)",
                        metrics=[
                            element.metric_duration(
                                statistic=_cloudwatch.Stats.AVERAGE),
                            element.metric_duration(
                                statistic=_cloudwatch.Stats.MAXIMUM)
                        ]
                    ),
                    _cloudwatch.GaugeWidget(
                        title=f"{element.function_name} Invocations",
                        metrics=[
                            element.metric_invocations(
                                statistic=_cloudwatch.Stats.AVERAGE)
                        ]
                    )
                )
            elif isinstance(element, _dynamoDB.Table):
                dashboard.add_widgets(
                    _cloudwatch.GraphWidget(
                        title=f"{element.table_name} Latencies",
                        right=[
                            element.metric_successful_request_latency(dimensions_map={
                                "TableName": element.table_name,
                                "Operation": "GetItem"
                            }),
                            element.metric_successful_request_latency(dimensions_map={
                                "TableName": element.table_name,
                                "Operation": "PutItem"
                            })
                        ],
                        width=12
                    )
                )
            else:
                print(type(element))
