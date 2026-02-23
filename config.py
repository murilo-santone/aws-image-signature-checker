import os
from dotenv import load_dotenv

# Carrega o arquivo .env
load_dotenv()

class Config:
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION','us-east-1')
    BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

    @staticmethod
    def validate():
        """
        Docstring for validate
        """
        if not all([Config.AWS_ACCESS_KEY, Config.AWS_SECRET_KEY, Config.BUCKET_NAME]):
            raise ValueError('Erro: Variáveis de ambiente faltando no arquivo .env')