# 🔎 Validador de Arquivos no AWS S3

Projeto desenvolvido em **Python** para validar em lote a existência de arquivos armazenados no **Amazon S3**, utilizando paginação e processamento paralelo para trabalhar com grandes volumes de registros.

A aplicação recebe uma base de dados contendo as chaves dos arquivos, consulta o bucket configurado e gera um relatório com o resultado das validações.

---

## 🎯 Objetivo

Automatizar a validação de grandes volumes de arquivos no Amazon S3, evitando verificações manuais e permitindo identificar rapidamente registros cujos arquivos existem ou não no bucket.

---

## ⚙️ Funcionamento

O processo executa as seguintes etapas:

1. Carrega os registros de entrada.
2. Processa os dados em lotes.
3. Consulta os arquivos no Amazon S3.
4. Utiliza processamento paralelo para acelerar as validações.
5. Consolida os resultados.
6. Gera um arquivo final com o status de cada registro.

---

## 🛠️ Tecnologias utilizadas

- Python
- Pandas
- Boto3
- Amazon S3
- ThreadPoolExecutor
- dotenv

---

## 📁 Estrutura do projeto

```text
.
├── main.py
├── services.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── tests/
```

---

## 🔐 Configuração

As credenciais e configurações da AWS são carregadas por variáveis de ambiente.

Crie um arquivo `.env` na raiz do projeto com base no arquivo `.env.example`:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name_here
```

> O arquivo `.env` contém informações sensíveis e não deve ser versionado. O repositório mantém apenas o `.env.example`, contendo valores de exemplo.

---

## 📦 Instalação

Clone o repositório:

```bash
git clone https://github.com/murilo-santone/aws-image-signature-checker.git
cd aws-image-signature-checker
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure o arquivo `.env` e execute:

```bash
python main.py
```

---

## ⚡ Processamento

O projeto utiliza paginação e processamento paralelo para permitir a validação de grandes volumes de registros sem carregar todo o processamento de uma única vez.

As consultas ao Amazon S3 são distribuídas entre múltiplas threads, reduzindo o tempo necessário para validar os arquivos.

---

## 📊 Resultado

Ao final da execução, é gerado um arquivo contendo os registros processados e o resultado da validação de cada arquivo no Amazon S3.

O projeto foi estruturado a partir de um cenário de validação em grande volume, com foco em automação, processamento em lote e integração com serviços AWS.

---

## 👨‍💻 Autor

**Murilo Santone**

[LinkedIn](https://www.linkedin.com/in/murilo-santone/)
