import requests
from supabase import create_client, Client
from datetime import datetime
from config import get_config

# Load configuration
config = get_config()

# config supabase
url: str = config.SUPABASE_URL
key: str = config.SUPABASE_KEY
supabase: Client = create_client(url, key)

# config api
API_URL = "https://data-api.polymarket.com/activity"
MAX_LIMIT = 500  # max limit of the api
TABLE_NAME = config.TABLE_NAME_TRADES

def transform_activity_to_db_format(activity: dict) -> dict:
    """
    Transforms API format to database format
    
    Args:
        activity: Dictionary with API data
    
    Returns:
        Dictionary formatted for database insertion
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
    db_activities = [transform_activity_to_db_format(activity) for activity in data]
    # print('db_activities', db_activities[0])
    print('===============================================')
    print('fetching activities from', user_address)
    print('db_activities length', len(db_activities))
    print('===============================================')
    return db_activities


def insert_activities_batch(activities: list):
    """
    Insert activities into the database, skipping duplicates.
    Uses upsert with unique_activity_key to avoid errors on re-polls.
    """
    if not activities:
        print("No activities to insert")
        return 0

    success_count = 0
    skip_count = 0
    for activity in activities:
        try:
            supabase.table(TABLE_NAME).upsert(
                activity, on_conflict="unique_activity_key"
            ).execute()
            success_count += 1
        except Exception as e:
            error_msg = str(e).lower()
            if 'duplicate' in error_msg or 'unique' in error_msg or 'conflict' in error_msg:
                skip_count += 1
            else:
                print(f"Error inserting activity: {e}")
    if skip_count:
        print(f"Skipped {skip_count} duplicate activities")
    return success_count

if __name__ == "__main__":
    user_address = input("Enter the user address: ")
    activities = fetch_activities(user_address)
    success_count = insert_activities_batch(activities)
    print(f"Success count: {success_count}")