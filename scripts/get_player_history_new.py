import requests
import os
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta

load_dotenv()

# config supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# config api
API_URL = "https://data-api.polymarket.com/activity"
MAX_LIMIT = 500  # max limit of the api
TABLE_NAME = "historic_trades"


def fetch_activities(user_address: str, limit: int = 500, offset: int = 0):
    """
    Fetch activities from the api
    """
    resp = requests.get(API_URL, params={
        "user": user_address,
        "limit": str(limit),
        "offset": str(offset),
        "sortBy": "TIMESTAMP",
        "sortDirection": "DESC",
    })

    data = resp.json()
    return data

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
