import pytest
from services import S3Service

# Teste Caminho Feliz
def test_transformacao_correta():
    entrada = 'signature:1620/2026/01/07/sig.jpg'
    esperado = 'signature/1620/2026/01/07/sig.jpg'
    assert S3Service.transform_db_key(entrada) == esperado

# Teste Sujeira (Espaços)
def test_remove_espacos():
    entrada = 'signature:1620'
    esperado = 'signature/1620'
    assert S3Service.transform_db_key(entrada) == esperado

# Teste Dados Ruins
def test_retorna_none_se_invalido():
    assert S3Service.transform_db_key(None) is None
    assert S3Service.transform_db_key(123) is None
      