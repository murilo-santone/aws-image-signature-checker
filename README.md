# S3 Signature Validator

Um utilitário de alta performance desenvolvido em Python para validação em massa (lote) de integridade de arquivos em buckets AWS S3. 

Este projeto foi desenhado para resolver o gargalo de auditar mais de 1.000.000 registros exportados de um banco de dados relacional, validando a existência física dos documentos na nuvem sem comprometer a memória da máquina e reduzindo o tempo de I/O de rede.

## 🏗️ Arquitetura e Estratégia

Para lidar com a alta volumetria de dados, a arquitetura foi baseada em três pilares:

1. **Memory Control (Paginação):** O dataset original é processado através do Pandas utilizando fatiamento (lotes de 5.000 registros). Isso impede o estouro de memória RAM (OOM) durante execuções prolongadas.
2. **Concorrência (Multi-threading):** O gargalo de I/O gerado pela latência de rede na comunicação com a AWS é mitigado utilizando o `ThreadPoolExecutor`. Cada lote abre dezenas de conexões simultâneas para validar as URIs.
3. **Fault Tolerance (Resiliência):** O pipeline possui programação defensiva. Exceções geradas por interrupções de rede ou dados corrompidos na origem (SQL) são capturadas individualmente por thread, impedindo a quebra do lote (Graceful Degradation).

## 🛠️ Tecnologias Utilizadas

- **Python 3.x:** Linguagem base.
- **Pandas:** Ingestão, tratamento estruturado e exportação de dados.
- **Boto3 (AWS SDK):** Interface de comunicação com o Amazon S3.
- **Concurrent.Futures:** Orquestração de threads.
- **Pytest:** Cobertura de testes unitários para regras de sanitização de strings.

## 🚀 Guia de Execução

### 1. Preparando o Ambiente
Recomenda-se a utilização de um ambiente virtual (venv). Instale as dependências executando:

```bash
pip install -r requirements.txt
```

### 2. Configuração de Credenciais
Crie um arquivo .env na raiz do diretório do projeto, baseando-se no arquivo .env.example:

```bash
AWS_ACCESS_KEY_ID=sua_chave_aqui
AWS_SECRET_ACCESS_KEY=seu_secret_aqui
AWS_REGION=us-east-1
S3_BUCKET_NAME=nome_do_seu_bucket
```

### 3. Execução
Com os arquivos de entrada (CSV) posicionados no diretório configurado, inicie o pipeline:
```bash
python main.py
```

O script fornecerá logs de progresso no terminal e, ao final, exportará um relatório .xlsx contendo exclusivamente os registros que falharam na validação (arquivos não encontrados ou erros de leitura).