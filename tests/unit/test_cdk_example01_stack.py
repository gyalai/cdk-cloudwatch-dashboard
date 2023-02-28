import aws_cdk as core
from demo_application.demo_application_stack import DemoApplicationStack


def cdk_nag():
    app = core.App()
    stack = DemoApplicationStack(app, "demo-application")




