#!/usr/bin/env python3
import aws_cdk as cdk

from cdk.config import Config
from cdk.repository import RepositoryStack
from cdk.pipeline import PipelineStack


app = cdk.App()

config = Config()
config.application.name = "my-demo-application"

RepositoryStack(app, "RepositoryStack", config)
PipelineStack(app, "PipelineStack", config)

app.synth()
