#!/usr/bin/env python3
import aws_cdk as cdk
import cdk_nag

from cdk.config import Config
from cdk.repository import RepositoryStack
from cdk.pipeline import PipelineStack
from demo_application.demo_application_stack import DemoApplicationStack
from cloudwatch_dashboard.dashboard import Dashboard


app = cdk.App()

config = Config()
config.application.name = "my-demo-application"

RepositoryStack(app, "RepositoryStack", config)
PipelineStack(app, "PipelineStack", config)


demo_stack = DemoApplicationStack(app, "demo-application-stack")

Dashboard(demo_stack, "my-Dashboard", "test")

cdk.Aspects.of(demo_stack).add(cdk_nag.AwsSolutionsChecks())

app.synth()
