from aws_cdk import (
    Stack,
    CfnOutput,
    aws_codecommit as _codecommit
)
from constructs import Construct
from cdk.config import Config

class RepositoryStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repository = _codecommit.Repository(self, "Repository", repository_name=config.application.name)

        self.repository_name = repository.repository_name

        CfnOutput(self, 'Repository Url', 
            value=repository.repository_clone_url_http,
            description=f"Url for the CodeCommit repository of the {config.application.name}"
        )

