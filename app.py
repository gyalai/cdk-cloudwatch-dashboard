#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_example01.cdk_example01_stack import CdkExample01Stack


app = cdk.App()
CdkExample01Stack(app, "cdk-example01")

app.synth()
