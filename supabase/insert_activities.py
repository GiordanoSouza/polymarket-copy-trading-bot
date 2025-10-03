import os
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

def fetch_polymarket_activities(user_address: str, limit: int = 10):
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

def insert_activities(activities: list):
    """
    Insere atividades no Supabase
    """
    transformed_activities = [transform_activity(act) for act in activities]
    
    try:
        # Inserir dados (upsert com base no transaction_hash)
        response = supabase.table("polymarket_activities").upsert(
            transformed_activities,
            on_conflict="transaction_hash"
        ).execute()
        
        print(f"✅ {len(transformed_activities)} atividades inseridas/atualizadas com sucesso!")
        return response
    except Exception as e:
        print(f"❌ Erro ao inserir atividades: {e}")
        raise

def main():
    # Endereço do usuário (Car/Peppery-Capital)
    user_address = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
    
    print(f"🔍 Buscando atividades do usuário {user_address}...")
    activities = fetch_polymarket_activities(user_address, limit=50)
    
    print(f"📊 Encontradas {len(activities)} atividades")
    
    if activities:
        print("💾 Inserindo no Supabase...")
        insert_activities(activities)
        
        # Mostrar resumo
        print("\n" + "="*80)
        print("RESUMO DAS ATIVIDADES INSERIDAS:")
        print("="*80)
        
        for i, act in enumerate(activities[:5], 1):  # Mostrar apenas as 5 primeiras
            act_time = datetime.fromtimestamp(act['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
            print(f"\n{i}. {act['type']} - {act_time}")
            if act['type'] == 'TRADE':
                print(f"   {act['side']}: {act['size']} @ ${act['price']:.6f}")
                print(f"   Mercado: {act.get('title', 'N/A')}")
        
        print(f"\n... e mais {len(activities) - 5} atividades" if len(activities) > 5 else "")
    else:
        print("⚠️ Nenhuma atividade encontrada")

if __name__ == "__main__":
    main()

