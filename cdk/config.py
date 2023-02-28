

class Config:

    def __init__(self) -> None:
        self.application = AppConfig()


class AppConfig:

    def __init__(self) -> None:
        self.name = 'MyApplication'
        self.branch_name = "main"
        self.tags = {
            "application-stack": self.name,
            "application-type": "Serverless"
        }