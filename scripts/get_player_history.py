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
    """Calculates the timestamp from 1 year ago"""
    one_year_ago = datetime.now() - timedelta(days=365)
    return int(one_year_ago.timestamp())

def fetch_activities(user_address: str, limit: int = 500, offset: int = 0):
    """
    Fetches user activities from Polymarket API
    
    Args:
        user_address: User wallet address
        limit: Maximum number of records per request (max 500)
        offset: Number of records to skip (pagination)
    
    Returns:
        List of activities or None in case of error
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
        print(f"❌ Request error (offset {offset}): {e}")
        return None

def transform_activity_to_db_format(activity: dict) -> dict:
    """
    Transforms API format to database format
    
    Args:
        activity: Dictionary with API data
    
    Returns:
        Dictionary formatted for database insertion
    """
    # Convert timestamp to datetime
    
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
    Inserts a batch of activities into Supabase
    
    Args:
        activities: List of activities formatted for the database
    
    Returns:
        Tuple (success, duplicates, errors)
    """

    
    if not activities:
        print("⚠️ No activities to insert")
        return None
    
    success_count = 0
    duplicate_count = 0
    error_count = 0
    
    for activity in activities:
        # Generate the compound unique key (same logic as computed column)
        condition_id = activity.get('condition_id') or 'null'
        price = str(activity.get('price')) if activity.get('price') is not None else 'null'
        unique_key = f"{activity['transaction_hash']}_{condition_id}_{price}"
        try:
            # Try to insert into database
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
            # Check if it's a duplicate error (transaction_hash UNIQUE)
            if 'duplicate' in error_msg or 'unique' in error_msg:
                duplicate_count += 1
            else:
                error_count += 1
                print(f"   ⚠️  Error inserting activity: {e}")
    
    return success_count, duplicate_count, error_count

def import_player_history(user_address: str, days_back: int = 365):
    """
    Imports all player history from the last N days
    
    Args:
        user_address: User wallet address
        days_back: Number of days to fetch from history (default: 365 = 1 year)
    """
    print("=" * 100)
    print(f"🚀 STARTING HISTORY IMPORT")
    print("=" * 100)
    print(f"📍 Player: {user_address}")
    print(f"📅 Period: Last {days_back} days")
    print(f"🗄️  Table: {TABLE_NAME}")
    print("=" * 100 + "\n")
    
    # Timestamp limit (1 year ago)
    timestamp_limit = int((datetime.now() - timedelta(days=days_back)).timestamp())
    
    offset = 0
    total_fetched = 0
    total_inserted = 0
    total_duplicates = 0
    total_errors = 0
    continue_fetching = True
    
    while continue_fetching:
        print(f"📥 Fetching activities (offset: {offset}, limit: {MAX_LIMIT})...")
        
        # Fetch activities from API
        activities = fetch_activities(user_address, limit=MAX_LIMIT, offset=offset)
        print('activities', activities[0])
        if not activities or len(activities) == 0:
            print(f"✅ No activities returned. End of pagination.\n")
            break
        
        print(f"   ✓ Received: {len(activities)} activities")
        total_fetched += len(activities)
        
        # Filter activities within the period
        activities_in_range = []
        for activity in activities:
            if activity.get('timestamp') and activity['timestamp'] >= timestamp_limit:
                activities_in_range.append(activity)
            else:
                # If we find an activity outside the period, stop the search
                continue_fetching = False
                break
        
        if len(activities_in_range) == 0:
            print(f"   ⏹️  All activities are outside the {days_back} days period.\n")
            break
        
        print(f"   ✓ In period: {len(activities_in_range)} activities")
        
        # Transform to database format
        db_activities = [transform_activity_to_db_format(act) for act in activities_in_range]
        
        # Insert into database
        print(f"   💾 Inserting into Supabase...")
        success, duplicates, errors = insert_activities_batch(db_activities)
        
        total_inserted += success
        total_duplicates += duplicates
        total_errors += errors
        
        print(f"   ✓ Inserted: {success} | Duplicates: {duplicates} | Errors: {errors}\n")
        
        # If we received less than the limit, we reached the end
        if len(activities) < MAX_LIMIT:
            print(f"✅ Last page reached (received {len(activities)} < {MAX_LIMIT}).\n")
            break
        
        # If no longer in the period of interest, stop
        if not continue_fetching:
            print(f"⏹️  Period of {days_back} days reached. Stopping search.\n")
            break
        
        # Next page
        offset += MAX_LIMIT
        
        # Small delay to not overload the API
        time.sleep(0.5)
    
    # Final summary
    print("=" * 100)
    print("📊 IMPORT SUMMARY")
    print("=" * 100)
    print(f"📥 Total activities fetched: {total_fetched}")
    print(f"✅ Total successfully inserted: {total_inserted}")
    print(f"🔄 Total duplicates (ignored): {total_duplicates}")
    print(f"❌ Total errors: {total_errors}")
    print("=" * 100 + "\n")

def import_multiple_players(user_addresses: list, days_back: int = 365):
    """
    Imports history for multiple players
    
    Args:
        user_addresses: List of wallet addresses
        days_back: Number of days to fetch from history
    """
    print("\n" + "=" * 100)
    print(f"🎯 IMPORT OF {len(user_addresses)} PLAYERS")
    print("=" * 100 + "\n")
    
    for i, address in enumerate(user_addresses, 1):
        print(f"\n{'🔹' * 50}")
        print(f"Player {i}/{len(user_addresses)}")
        print(f"{'🔹' * 50}\n")
        
        import_player_history(address, days_back)
        
        # Delay between players
        if i < len(user_addresses):
            time.sleep(1)
    
    print("\n" + "=" * 100)
    print("🎉 IMPORT OF ALL PLAYERS COMPLETED!")
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

