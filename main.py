import pandas as pd
import os
import concurrent.futures # Biblioteca do Paralelismo
from datetime import datetime
from config import Config
from services import S3Service

# --- CONFIGURAÇÕES ---
PASTA_SAIDA = 'C:/Temp/auditoria_validacao_assinatura'
ARQUIVO_ENTRADA = 'C:/Temp/export_assinaturas_sql_0101_a_3112_2022.csv'

# CONFIGURAÇÃO DE PERFORMANCE
MAX_WORKERS = 50 # Quantidade threads simultâneas (Internet)
TAMANHO_LOTE = 5000 # Quantidade linhas processar por vez (Memória) 

# --- A FUNÇÃO DO "TRABALHADOR" ---
# Esta função valida UMA única linha. O Executor vai chamar ela em paralelo.
def processar_uma_linha(row, validator_instance):
    """
    Recebe uma linha do DataFrame e a instância do validador.
    Retorna um dicionário se der ERRO, ou None se der SUCESSO.
    """
    try:
        raw_sig = row.get('cCustomerSignature')
        invoice_id = row.get('cIDInvoice')
        
        # 1. Blindagem contra vazio
        if pd.isna(raw_sig) or str(raw_sig).strip() == '':
            return None # Pula se não tiver erro no dataframe
            
        # 2. Validação S3
        status = validator_instance.check_file_exists(raw_sig)
        
        # 3. Se NÃO existir, retorna os dados do erro
        if not status.get('exists', False):
            return {
                'Data_Emissao': row.get('dEmission'),
                'Invoice': invoice_id,
                'Serie': row.get('cSerie'),
                'Centro': row.get('cIDBranchInvoice'),
                'Cliente': row.get('cIDCustomer'),
                'Viagem': row.get('cIDTrip'),
                'Veiculo': row.get('cIDUserLastUpdate'),
                'Data_Banco': raw_sig,
                'Caminho_Testado_S3': status.get('key', 'Desconhecido'),
                'Motivo_Erro': status.get('reason', 'Arquivo não localizado no S3')
            }
            
        return None # Se existir, retorna nada (para economizar memória)
        
    except Exception as e:
        # Se der erro no código dentro da thread, capturamos aqui para não parar tudo
        return {
            'Data_Emissao': None,
            'Invoice': row.get('cIDInvoice', 'Unknown') if isinstance(row, pd.Series) else 'Erro',
            'Serie': row.get('cSerie', 'Unknown') if isinstance(row, pd.Series) else 'Erro',
            'Centro': row.get('cIDBranchInvoice', 'Unknown') if isinstance(row, pd.Series) else 'Erro',
            'Cliente': None,
            'Viagem': row.get('cIDTrip', 'Unknown') if isinstance(row, pd.Series) else 'Erro',
            'Veiculo': row.get('cIDUserLastUpdate', 'Unknown') if isinstance(row, pd.Series) else 'Erro',
            'Data_Banco': row.get('cCustomerSignature', 'Unknown') if isinstance(row, pd.Series) else 'Erro',
            'Caminho_Testado_S3': 'N/A',
            'Motivo_Erro': f"ERRO_PYTHON_INTERNO: {str(e)}"
        }

# --- ORQUESTRAÇÃO (MAIN) ---
def main():
    print(f"🚀 Iniciando Auditoria Turbo (Paralelismo: {MAX_WORKERS} threads)...")
    print(f"⚙️ Config: {MAX_WORKERS} Threads | Lotes de {TAMANHO_LOTE} registros")

    # 1. Setup
    try:
        Config.validate()
        os.makedirs(PASTA_SAIDA, exist_ok=True)
    except ValueError as e:
        print(e)
        return

    # 2. Leitura
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"❌ Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return

    print("📖 Carregando Arquivo na memória (pode levar alguns segundos)...")    
    try:
        df = pd.read_csv(
            ARQUIVO_ENTRADA,  
            sep=';',            # Separador
            header=0,           # Linha 0 é sempre o cabeçalho
            dtype=str,          # Tudo como texto
            encoding='utf-16'   # Encoding do SQL Server (Unicode)
            )
        total_registros = len(df)
        print(f"📊 Total de registros: {len(df)}")
    except Exception as e:
        print(f"❌ Erro fatal ao ler Arquivo. Verifique encoding/separador.\nDetalhe: {e}")        
        return

    # 3. Execução Paralela
    validator = S3Service()
    lista_erros = []
    lotes_processados = 0
    total_lotes = (total_registros // TAMANHO_LOTE) + 1

    print(f"\n⚡ Iniciando validação de {total_lotes} lotes...")

    # Loop que "fatia" o DataFrane de 5.000 em 5.000
    for inicio in range(0, total_registros, TAMANHO_LOTE):
        fim = inicio + TAMANHO_LOTE

        # Cria e fatia (o lote atual)
        df_lote = df.iloc[inicio:fim]
        lotes_processados += 1

        # Processa este lote em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Cria as tarefas
            futures = [executor.submit(processar_uma_linha, row, validator) for _, row in df_lote.iterrows()]

            # Coleta os resultados conforme ficam prontos
            for future in concurrent.futures.as_completed(futures):
                resultado = future.result()
                if resultado: # Se voltou algo, é erro
                    lista_erros.append(resultado)

        # Feedback visual a cada lote finalizado
        print(f"   ✅ Lote {lotes_processados}/{total_lotes} concluído. (Erros acumulados: {len(lista_erros)})") 

    # 4. Geração do Relatório Final
    print("\n🏁 Processamento finalizado. Gerando relatório...")

    if lista_erros:
        # Gera nome com data e hora (timestamp)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome_arquivo = f'relatorio_erros_assinatura_{timestamp}.xlsx'
        caminho_final = os.path.join(PASTA_SAIDA, nome_arquivo)

        df_erros = pd.DataFrame(lista_erros)
        
        try:
            df_erros.to_excel(caminho_final, index=False)
            print(f"⚠️ Encontrados {len(lista_erros)} erros.")
            print(f"📄 Relatório salvo em:\n   👉 {caminho_final}")
        except PermissionError:
            print("❌ ERRO AO SALVAR: O arquivo Excel parece estar aberto ou sem permissão.")
            # Fallback: Tenta salvar com outro nome se der erro
            df_erros.to_csv(os.path.join(PASTA_SAIDA, f"resgate_{timestamp}.csv"), sep=';', index=False)
    else:
        print("\n🏆 SUCESSO! Todas as assinaturas foram validadas e existem no S3.")

if __name__ == "__main__":
    main()