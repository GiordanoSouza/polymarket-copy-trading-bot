import os
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import requests

# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidos no arquivo .env")

supabase: Client = create_client(url, key)

def fetch_polymarket_activities(user_address: str, limit: int = 50):
    """
    Busca atividades de um usuário no Polymarket
    """
    url = "https://data-api.polymarket.com/activity"
    resp = requests.get(url, params={
        "user": user_address,
        "limit": str(limit),
        "sortBy": "TIMESTAMP",
        "sortDirection": "DESC",
    })
    return resp.json()

def transform_activity(activity: dict) -> dict:
    """
    Transforma os dados da API para o formato da tabela do Supabase
    """
    # Converter timestamp para datetime
    activity_datetime = datetime.fromtimestamp(activity['timestamp'])
    
    return {
        "proxy_wallet": activity.get("proxyWallet"),
        "timestamp": activity.get("timestamp"),
        "activity_datetime": activity_datetime.isoformat(),
        "condition_id": activity.get("conditionId"),
        "type": activity.get("type"),
        "size": activity.get("size"),
        "usdc_size": activity.get("usdcSize"),
        "transaction_hash": activity.get("transactionHash"),
        "price": activity.get("price"),
        "asset": activity.get("asset"),
        "side": activity.get("side"),
        "outcome_index": activity.get("outcomeIndex"),
        "title": activity.get("title"),
        "slug": activity.get("slug"),
        "icon": activity.get("icon"),
        "event_slug": activity.get("eventSlug"),
        "outcome": activity.get("outcome"),
        "trader_name": activity.get("name"),
        "pseudonym": activity.get("pseudonym"),
        "bio": activity.get("bio"),
        "profile_image": activity.get("profileImage"),
        "profile_image_optimized": activity.get("profileImageOptimized"),
    }

def insert_activities_batch(activities: list):
    """
    Insere atividades no Supabase em lote, ignorando duplicatas
    """
    if not activities:
        return {"inserted": 0, "skipped": 0}
    
    transformed_activities = [transform_activity(act) for act in activities]
    inserted_count = 0
    skipped_count = 0
    
    for activity in transformed_activities:
        # Gerar a chave única composta (mesma lógica da coluna computed)
        condition_id = activity.get('condition_id') or 'null'
        price = str(activity.get('price')) if activity.get('price') is not None else 'null'
        unique_key = f"{activity['transaction_hash']}_{condition_id}_{price}"
        
        try:
            # Verificar se já existe
            existing = supabase.table("polymarket_activities").select("id").eq(
                "unique_activity_key", unique_key
            ).execute()
            
            if not existing.data:
                # Inserir apenas se não existir
                supabase.table("polymarket_activities").insert(activity).execute()
                inserted_count += 1
            else:
                skipped_count += 1
                
        except Exception as e:
            # Se der erro de unique constraint, é porque já existe
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                skipped_count += 1
            else:
                print(f"⚠️ Erro ao inserir atividade: {e}")
                # Continua com as próximas atividades
    
    return {"inserted": inserted_count, "skipped": skipped_count}

def get_latest_timestamp():
    """
    Busca o timestamp da atividade mais recente no banco
    """
    try:
        result = supabase.table("polymarket_activities").select("timestamp").order(
            "timestamp", desc=True
        ).limit(1).execute()
        
        if result.data:
            return result.data[0]['timestamp']
        return 0
    except Exception as e:
        print(f"⚠️ Erro ao buscar último timestamp: {e}")
        return 0

def poll_activities(user_address: str, interval_seconds: int = 60, limit: int = 100):
    """
    Faz polling contínuo das atividades do usuário
    
    Args:
        user_address: Endereço da carteira do usuário
        interval_seconds: Intervalo entre consultas (segundos)
        limit: Número de atividades a buscar por vez
    """
    print(f"🚀 Iniciando polling para {user_address}")
    print(f"⏱️  Intervalo: {interval_seconds}s | Limite por consulta: {limit}")
    print("-" * 80)
    
    poll_count = 0
    
    try:
        while True:
            poll_count += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\n[{current_time}] 📊 Poll #{poll_count}")
            
            try:
                # Buscar atividades da API
                activities = fetch_polymarket_activities(user_address, limit)
                
                if not activities:
                    print("   ℹ️  Nenhuma atividade encontrada")
                else:
                    # Inserir no banco (ignorando duplicatas)
                    result = insert_activities_batch(activities)
                    
                    if result['inserted'] > 0:
                        print(f"   ✅ {result['inserted']} novas atividades inseridas")
                    
                    if result['skipped'] > 0:
                        print(f"   ⏭️  {result['skipped']} atividades já existiam (ignoradas)")
                    
                    # Mostrar a atividade mais recente se houver inserções
                    if result['inserted'] > 0 and activities:
                        latest = activities[0]
                        act_time = datetime.fromtimestamp(latest['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
                        print(f"   📈 Última: {latest['type']} - {latest.get('title', 'N/A')[:50]}... ({act_time})")
                
            except Exception as e:
                print(f"   ❌ Erro no poll: {e}")
            
            # Aguardar próximo intervalo
            print(f"   ⏳ Aguardando {interval_seconds}s até próximo poll...")
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\n⛔ Polling interrompido pelo usuário")
        print(f"📊 Total de polls realizados: {poll_count}")

def main():
    """
    Função principal - configurar e iniciar o polling
    """
    # Configurações
    USER_ADDRESS = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"  # Car/Peppery-Capital
    INTERVAL_SECONDS = 60  # Polling a cada 60 segundos (1 minuto)
    LIMIT = 500  # Buscar até 100 atividades por poll
    
    print("\n" + "="*80)
    print("🎯 POLYMARKET ACTIVITY POLLING - COPY TRADING")
    print("="*80)
    print(f"Usuário: {USER_ADDRESS}")
    print(f"Intervalo: {INTERVAL_SECONDS}s")
    print(f"Limite por consulta: {LIMIT}")
    print("="*80)
    
    # Mostrar estatísticas iniciais
    latest_ts = get_latest_timestamp()
    if latest_ts:
        latest_date = datetime.fromtimestamp(latest_ts).strftime('%d/%m/%Y %H:%M:%S')
        print(f"📅 Última atividade no banco: {latest_date}")
    else:
        print("📅 Banco vazio - primeira execução")
    
    print("\n💡 Pressione Ctrl+C para parar o polling\n")
    
    # Iniciar polling
    poll_activities(USER_ADDRESS, INTERVAL_SECONDS, LIMIT)

if __name__ == "__main__":
    main()


