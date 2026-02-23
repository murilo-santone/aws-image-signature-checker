import boto3
from botocore.exceptions import ClientError
from config import Config
import pandas as pd

class S3Service:
    def __init__(self):
        """
        Docstring for __init__
        
        :param self: Description
        """
        self.client = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY,
            region_name=Config.AWS_REGION
        )
        self.bucket = Config.BUCKET_NAME

    @staticmethod
    def transform_db_key(db_value: str) -> str:
        """
        Transforma a string do banco no caminho físico do S3.
        Lógica: Troca ':' por '/' e remove espaços.
        Ex: 'signature:123/2026/...' -> 'signature/123/2026/...'
        """
        # Guard Clause
        if pd.isna(db_value) or not isinstance(db_value, str):
            return None
        
        return db_value.replace(':','/').strip()

    def check_file_exists(self, raw_db_string: str) -> dict:
        """Verifica se o arquivo existe no Bucket"""

        s3_key = self.transform_db_key(raw_db_string)

        if not s3_key:
            {'exists':False,'reason':'DADO_INVALIDO','key':None}

        try:
            self.client.head_object(Bucket=self.bucket, Key=s3_key)
            return {'exists': True, 'reason': 'ENCONTRADO','key':s3_key}
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return {'exists':False, 'reason':'NAO_ENCONTRADO_404', 'key':s3_key}
            elif error_code == '403':
                return {'exists':False, 'reason':'SEM_PERMISSAO_403', 'key':s3_key}
            else:
                return {'exists':False, 'reason':f'ERRO_AWS_{error_code}', 'key':s3_key}