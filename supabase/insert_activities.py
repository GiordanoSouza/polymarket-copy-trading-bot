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

def fetch_polymarket_activities(user_address: str, limit: int = 500, offset: int = 0):
    """
    Busca atividades de um usuário no Polymarket
    """
    url = "https://data-api.polymarket.com/activity"
    resp = requests.get(url, params={
        "user": user_address,
        "limit": str(limit),
        "offset": str(offset),
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
    Insere atividades no Supabase usando upsert baseado na unique_activity_key
    """
    transformed_activities = [transform_activity(act) for act in activities]
    
    if not transformed_activities:
        print("⚠️ Nenhuma atividade para inserir")
        return None
    
    try:
        # Fazer upsert individual para cada atividade
        # Isso evita duplicatas baseado na unique_activity_key
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
                    raise
        
        print(f"✅ {inserted_count} atividades inseridas | {skipped_count} já existiam (puladas)")
        return {"inserted": inserted_count, "skipped": skipped_count}
        
    except Exception as e:
        print(f"❌ Erro ao inserir atividades: {e}")
        raise

def fetch_all_activities(user_address: str, total_records: int = 500):
    """
    Busca múltiplas páginas de atividades usando paginação
    
    Args:
        user_address: Endereço da carteira do usuário
        total_records: Total de registros a buscar (em múltiplos de 500)
    
    Returns:
        Lista com todas as atividades buscadas
    """
    all_activities = []
    batch_size = 500  # API retorna no máximo 500 por vez
    
    # Calcular quantas requisições são necessárias
    num_requests = (total_records + batch_size - 1) // batch_size
    
    print(f"📥 Buscando {total_records} registros em {num_requests} requisição(ões)...")
    
    for i in range(num_requests):
        offset = i * batch_size
        limit = min(batch_size, total_records - offset)
        
        print(f"   → Página {i+1}/{num_requests} (offset={offset}, limit={limit})...")
        
        activities = fetch_polymarket_activities(user_address, limit=limit, offset=offset)
        
        if not activities:
            print(f"   ⚠️ Nenhuma atividade retornada na página {i+1}")
            break
        
        all_activities.extend(activities)
        print(f"   ✓ {len(activities)} atividades obtidas (total acumulado: {len(all_activities)})")
        
        # Se retornou menos que o limite, não há mais dados
        if len(activities) < limit:
            print(f"   ℹ️ Última página alcançada")
            break
    
    return all_activities

def main():
    # Endereço do usuário (Car/Peppery-Capital)
    user_address = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
    
    # ============================================================
    # CONFIGURAÇÃO: Altere aqui quantos registros quer buscar
    # ============================================================
    TOTAL_RECORDS_TO_FETCH = 1500  # Pode ser 500, 1000, 1500, etc.
    # ============================================================
    
    print("="*80)
    print(f"🎯 CONFIGURAÇÃO: Buscando {TOTAL_RECORDS_TO_FETCH} registros")
    print("="*80)
    print(f"👤 Usuário: {user_address}\n")
    
    # Buscar atividades com paginação
    activities = fetch_all_activities(user_address, total_records=TOTAL_RECORDS_TO_FETCH)
    
    print(f"\n📊 Total de atividades obtidas: {len(activities)}")
    
    if activities:
        print("\n💾 Inserindo no Supabase...")
        result = insert_activities(activities)
        
        # Mostrar resumo
        print("\n" + "="*80)
        print("RESUMO DAS ATIVIDADES:")
        print("="*80)
        
        if result:
            print(f"✅ Inseridas: {result['inserted']}")
            print(f"⏭️  Puladas (duplicadas): {result['skipped']}")
        
        print("\n📋 Primeiras 5 atividades:")
        print("-"*80)
        
        for i, act in enumerate(activities[:5], 1):  # Mostrar apenas as 5 primeiras
            act_time = datetime.fromtimestamp(act['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
            print(f"\n{i}. {act['type']} - {act_time}")
            if act['type'] == 'TRADE':
                print(f"   {act['side']}: {act['size']} @ ${act['price']:.6f}")
                print(f"   Mercado: {act.get('title', 'N/A')}")
            print(f"   Hash: {act.get('transactionHash', 'N/A')}")
        
        print(f"\n... e mais {len(activities) - 5} atividades" if len(activities) > 5 else "")
        
        # Análise de duplicatas
        print("\n" + "="*80)
        print("🔍 ANÁLISE DE DUPLICATAS:")
        print("="*80)
        
        # Contar por transaction_hash
        tx_hashes = {}
        for act in activities:
            tx_hash = act.get('transactionHash', 'unknown')
            tx_hashes[tx_hash] = tx_hashes.get(tx_hash, 0) + 1
        
        duplicated_txs = {k: v for k, v in tx_hashes.items() if v > 1}
        
        if duplicated_txs:
            print(f"\n⚠️ Encontrados {len(duplicated_txs)} transaction_hash com múltiplas atividades:")
            for tx_hash, count in sorted(duplicated_txs.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   • {tx_hash[:20]}... → {count} atividades")
                # Mostrar detalhes dessas atividades
                duped_acts = [a for a in activities if a.get('transactionHash') == tx_hash]
                for act in duped_acts[:3]:  # Mostrar até 3
                    print(f"      - {act['type']} | conditionId: {act.get('conditionId', 'N/A')} | price: {act.get('price', 'N/A')}")
        else:
            print("✅ Nenhum transaction_hash duplicado encontrado")
        
    else:
        print("⚠️ Nenhuma atividade encontrada")

if __name__ == "__main__":
    main()

