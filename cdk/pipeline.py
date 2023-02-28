from aws_cdk import (
    Stack,
    pipelines,
    aws_codecommit as _codecommit,
    aws_codebuild as _codebuild
)
from cdk.config import Config
from cdk.application_stage import ApplicationStage
from constructs import Construct


class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Pipeline
        repository = _codecommit.Repository.from_repository_name(
            self, "repository", config.application.name)

        code_commit_repository_source = pipelines.CodePipelineSource.code_commit(
            repository, config.application.branch_name)

        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            pipeline_name=config.application.name,
            cross_account_keys=False,
            self_mutation=True,

            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=_codebuild.BuildEnvironment(
                    compute_type=_codebuild.ComputeType.SMALL
                )
            ),

            synth=pipelines.ShellStep(
                "Synth",
                input=code_commit_repository_source,
                install_commands=[
                    "pip install -r requirements.txt",
                    "npm install -g aws-cdk"
                ],
                commands=[
                    "cdk synth"
                ]
            )
        )

        print(kwargs)

        stage = ApplicationStage(self, "Dev", app_config=config.application)

        pipeline.add_stage(stage)
