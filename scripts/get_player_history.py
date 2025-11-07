'''
OLDER VERSION OF THE SCRIPT
USE get_player_history_new.py FOR THE NEW VERSION
'''
import requests
from datetime import datetime, timedelta
import time
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuração do Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Configurações da API
API_URL = "https://data-api.polymarket.com/activity"
MAX_LIMIT = 500  # Limite máximo da API
TABLE_NAME = "historic_trades"

def get_timestamp_one_year_ago():
    """Calcula o timestamp de 1 ano atrás"""
    one_year_ago = datetime.now() - timedelta(days=365)
    return int(one_year_ago.timestamp())

def fetch_activities(user_address: str, limit: int = 500, offset: int = 0):
    """
    Busca atividades de um usuário na API do Polymarket
    
    Args:
        user_address: Endereço da carteira do usuário
        limit: Número máximo de registros por requisição (máx 500)
        offset: Número de registros para pular (paginação)
    
    Returns:
        Lista de atividades ou None em caso de erro
    """
    try:
        params = {
            "user": user_address,
            "limit": str(limit),
            "offset": str(offset),
            "sortBy": "TIMESTAMP",
            "sortDirection": "DESC",
        }
        
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição (offset {offset}): {e}")
        return None

def transform_activity_to_db_format(activity: dict) -> dict:
    """
    Transforma o formato da API para o formato do banco de dados
    
    Args:
        activity: Dicionário com dados da API
    
    Returns:
        Dicionário formatado para inserção no banco
    """
    # Converter timestamp para datetime
    
    activity_datetime = datetime.fromtimestamp(activity['timestamp'])
    
    return {
        'proxy_wallet': activity.get('proxyWallet'),
        'timestamp': activity.get('timestamp'),
        'activity_datetime': activity_datetime.isoformat(),
        'condition_id': activity.get('conditionId'),
        'type': activity.get('type'),
        'size': activity.get('size'),
        'usdc_size': activity.get('usdcSize'),
        'transaction_hash': activity.get('transactionHash'),
        'price': activity.get('price'),
        'asset': activity.get('asset'),
        'side': activity.get('side'),
        'outcome_index': activity.get('outcomeIndex'),
        'title': activity.get('title'),
        'slug': activity.get('slug'),
        'icon': activity.get('icon'),
        'event_slug': activity.get('eventSlug'),
        'outcome': activity.get('outcome'),
        'trader_name': activity.get('name'),
        'pseudonym': activity.get('pseudonym'),
        'bio': activity.get('bio'),
        'profile_image': activity.get('profileImage'),
        'profile_image_optimized': activity.get('profileImageOptimized'),
    }

def insert_activities_batch(activities: list):
    """
    Insere um lote de atividades no Supabase
    
    Args:
        activities: Lista de atividades formatadas para o banco
    
    Returns:
        Tupla (sucesso, duplicados, erros)
    """

    
    if not activities:
        print("⚠️ Nenhuma atividade para inserir")
        return None
    
    success_count = 0
    duplicate_count = 0
    error_count = 0
    
    for activity in activities:
        # Gerar a chave única composta (mesma lógica da coluna computed)
        condition_id = activity.get('condition_id') or 'null'
        price = str(activity.get('price')) if activity.get('price') is not None else 'null'
        unique_key = f"{activity['transaction_hash']}_{condition_id}_{price}"
        try:
            # Tentar inserir no banco
            existing = supabase.table(TABLE_NAME).select("id").eq(
                    "unique_activity_key", unique_key
                ).execute()
            
            if not existing.data:
                supabase.table(TABLE_NAME).insert(activity).execute()
                success_count += 1
            else:
                duplicate_count += 1
                
        except Exception as e:
            error_msg = str(e).lower()
            # Verificar se é erro de duplicata (transaction_hash UNIQUE)
            if 'duplicate' in error_msg or 'unique' in error_msg:
                duplicate_count += 1
            else:
                error_count += 1
                print(f"   ⚠️  Erro ao inserir atividade: {e}")
    
    return success_count, duplicate_count, error_count

def import_player_history(user_address: str, days_back: int = 365):
    """
    Importa todo o histórico de um player dos últimos N dias
    
    Args:
        user_address: Endereço da carteira do usuário
        days_back: Número de dias para buscar no histórico (padrão: 365 = 1 ano)
    """
    print("=" * 100)
    print(f"🚀 INICIANDO IMPORTAÇÃO DE HISTÓRICO")
    print("=" * 100)
    print(f"📍 Player: {user_address}")
    print(f"📅 Período: Últimos {days_back} dias")
    print(f"🗄️  Tabela: {TABLE_NAME}")
    print("=" * 100 + "\n")
    
    # Timestamp limite (1 ano atrás)
    timestamp_limit = int((datetime.now() - timedelta(days=days_back)).timestamp())
    
    offset = 0
    total_fetched = 0
    total_inserted = 0
    total_duplicates = 0
    total_errors = 0
    continue_fetching = True
    
    while continue_fetching:
        print(f"📥 Buscando atividades (offset: {offset}, limit: {MAX_LIMIT})...")
        
        # Buscar atividades da API
        activities = fetch_activities(user_address, limit=MAX_LIMIT, offset=offset)
        print('activities', activities[0])
        if not activities or len(activities) == 0:
            print(f"✅ Nenhuma atividade retornada. Fim da paginação.\n")
            break
        
        print(f"   ✓ Recebidas: {len(activities)} atividades")
        total_fetched += len(activities)
        
        # Filtrar atividades dentro do período de 1 ano
        activities_in_range = []
        for activity in activities:
            if activity.get('timestamp') and activity['timestamp'] >= timestamp_limit:
                activities_in_range.append(activity)
            else:
                # Se encontramos uma atividade fora do período, paramos a busca
                continue_fetching = False
                break
        
        if len(activities_in_range) == 0:
            print(f"   ⏹️  Todas as atividades estão fora do período de {days_back} dias.\n")
            break
        
        print(f"   ✓ No período: {len(activities_in_range)} atividades")
        
        # Transformar para formato do banco
        db_activities = [transform_activity_to_db_format(act) for act in activities_in_range]
        
        # Inserir no banco
        print(f"   💾 Inserindo no Supabase...")
        success, duplicates, errors = insert_activities_batch(db_activities)
        
        total_inserted += success
        total_duplicates += duplicates
        total_errors += errors
        
        print(f"   ✓ Inseridos: {success} | Duplicados: {duplicates} | Erros: {errors}\n")
        
        # Se recebemos menos que o limite, chegamos ao fim
        if len(activities) < MAX_LIMIT:
            print(f"✅ Última página alcançada (recebidas {len(activities)} < {MAX_LIMIT}).\n")
            break
        
        # Se não está mais no período de interesse, parar
        if not continue_fetching:
            print(f"⏹️  Período de {days_back} dias alcançado. Parando busca.\n")
            break
        
        # Próxima página
        offset += MAX_LIMIT
        
        # Pequeno delay para não sobrecarregar a API
        time.sleep(0.5)
    
    # Resumo final
    print("=" * 100)
    print("📊 RESUMO DA IMPORTAÇÃO")
    print("=" * 100)
    print(f"📥 Total de atividades buscadas: {total_fetched}")
    print(f"✅ Total inseridas com sucesso: {total_inserted}")
    print(f"🔄 Total de duplicadas (ignoradas): {total_duplicates}")
    print(f"❌ Total de erros: {total_errors}")
    print("=" * 100 + "\n")

def import_multiple_players(user_addresses: list, days_back: int = 365):
    """
    Importa o histórico de múltiplos players
    
    Args:
        user_addresses: Lista de endereços de carteiras
        days_back: Número de dias para buscar no histórico
    """
    print("\n" + "=" * 100)
    print(f"🎯 IMPORTAÇÃO DE {len(user_addresses)} PLAYERS")
    print("=" * 100 + "\n")
    
    for i, address in enumerate(user_addresses, 1):
        print(f"\n{'🔹' * 50}")
        print(f"Player {i}/{len(user_addresses)}")
        print(f"{'🔹' * 50}\n")
        
        import_player_history(address, days_back)
        
        # Delay entre players
        if i < len(user_addresses):
            time.sleep(1)
    
    print("\n" + "=" * 100)
    print("🎉 IMPORTAÇÃO DE TODOS OS PLAYERS CONCLUÍDA!")
    print("=" * 100 + "\n")

# Example usage
if __name__ == "__main__":
    # ============================================================
    # Player configuration
    # ============================================================
    
    # Example with a single player
    player_address = input("Enter player wallet address: ")
    if player_address:
        days_back = int(input("Enter days of history to fetch (default 365): ") or "365")
        import_player_history(player_address, days_back=days_back)
    else:
        print("No player address provided.")
    
    # Or import multiple players at once
    # players = [
    #     "0x1234...abcd",  # Replace with actual addresses
    #     "0x5678...efgh",
    #     "0x9abc...ijkl",
    # ]
    # import_multiple_players(players, days_back=365)

