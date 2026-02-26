# Code to get player positions and detect if any position exceeds the defined limit
import requests
from supabase import create_client, Client
from config import get_config

# Load configuration
config = get_config()

# config supabase
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

API_URL = 'https://data-api.polymarket.com/positions'
MAX_LIMIT = 500  # Limite máximo da API
TABLE_NAME = config.TABLE_NAME_POSITIONS

def fetch_player_positions(user_address: str, limit: int = 500, offset: int = 0, condition_id: str = None):
    try:
        params = {
            "user": user_address,
            "limit": str(limit),
            "offset": str(offset),
            "sortBy": "INITIAL",
            "sortDirection": "DESC",
        }
        # Only include conditionId when there is a value
        if condition_id is not None:
            params["conditionId"] = condition_id
        
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        # print('data', data)
        print('===============================================')
        print('fetching positions from', user_address)
        print('===============================================')
        print('data length', len(data))
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error (offset {offset}): {e}")
        return None



def transform_position_to_db_format(position: dict) -> dict:
    """
    Transforms API format to database format
    
    Args:
        position: Dictionary with API data
    
    Returns:
        Dictionary formatted for database insertion
    """
    # Handle end_date: convert empty string or None to NULL
    end_date = position.get('endDate')
    if not end_date or end_date == '':
        end_date = None
    
    # Handle eventId: convert string to int, or None if empty
    event_id = position.get('eventId')
    if event_id:
        try:
            event_id = int(event_id)
        except (ValueError, TypeError):
            event_id = None
    else:
        event_id = None
    
    return {
       'proxy_wallet': position.get('proxyWallet'),
       'asset': position.get('asset'),
       'condition_id': position.get('conditionId'),
       'size': position.get('size'),
       'avg_price': position.get('avgPrice'),
       'initial_value': position.get('initialValue'),
       'current_value': position.get('currentValue'),
       'cash_pnl': position.get('cashPnl'),
       'percent_pnl': position.get('percentPnl'),
       'total_bought': position.get('totalBought'),
       'realized_pnl': position.get('realizedPnl'),
       'percent_realized_pnl': position.get('percentRealizedPnl'),
       'cur_price': position.get('curPrice'),
       'redeemable': position.get('redeemable'),
       'mergeable': position.get('mergeable'),
       'title': position.get('title'),
       'slug': position.get('slug'),
       'icon': position.get('icon'),
       'event_id': event_id,
       'event_slug': position.get('eventSlug'),
       'outcome': position.get('outcome'),
       'outcome_index': position.get('outcomeIndex'),
       'opposite_outcome': position.get('oppositeOutcome'),
       'opposite_asset': position.get('oppositeAsset'),
       'end_date': end_date,
       'negative_risk': position.get('negativeRisk'),
    }

def insert_player_positions_batch(positions: list):
    """
    Inserts or updates positions only if there are significant changes.
    Compares with existing data to avoid unnecessary UPDATEs.
    """
    if not positions:
        print("No positions to insert")
        return 0

    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for idx, position in enumerate(positions, 1):
        try:
            # Transform to database format
            db_position = transform_position_to_db_format(position)
            asset_id = db_position['asset']
            proxy_wallet = db_position['proxy_wallet']
            
            # Search for existing record in database
            existing = supabase.table(TABLE_NAME).select("*").eq(
                "asset", asset_id
            ).eq(
                "proxy_wallet", proxy_wallet
            ).execute()
            
            # If doesn't exist, INSERT
            if not existing.data or len(existing.data) == 0:
                supabase.table(TABLE_NAME).insert(db_position).execute()
                success_count += 1
                print(f"➕ New position inserted: {db_position['title'][:50]}")
            else:
                # Exists, check if there was a change
                old_data = existing.data[0]
                
                # Important fields to compare
                fields_to_compare = [
                    'size',
                ]
                
                # Check if any field changed
                has_changes = False
                for field in fields_to_compare:
                    old_val = old_data.get(field)
                    new_val = db_position.get(field)
                    
                    # Compare with tolerance for floats
                    if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                        if abs(old_val - new_val) > 0.1:  # Tolerance of 0.1
                            has_changes = True
                            print(f"🔄 Change detected in '{field}': {old_val} → {new_val}")
                            break
                    elif old_val != new_val:
                        has_changes = True
                        print(f"🔄 Change detected in '{field}': {old_val} → {new_val}")
                        break
                
                # Only UPDATE if there are changes
                if has_changes:
                    supabase.table(TABLE_NAME).update(db_position).eq(
                        "asset", asset_id
                    ).eq(
                        "proxy_wallet", proxy_wallet
                    ).execute()
                    success_count += 1
                    print(f"🔄 Position updated: {db_position['title'][:50]}")
                else:
                    skipped_count += 1
                    # print(f"⏭️  Position unchanged: {db_position['title'][:50]}")
                    
        except Exception as e:
            error_count += 1
            print(f"❌ Error in position {idx}/{len(positions)}: {e}")
            print(f"   Title: {position.get('title', 'N/A')}")
            print(f"   Asset: {position.get('asset', 'N/A')[:20]}...")
            # Continue processing next positions
    
    print(f"\n✅ Summary: {success_count} inserted/updated, {skipped_count} unchanged, {error_count} with error")
    return success_count




def print_positions_readable(positions: list):
    if not positions:
        print("\n⚠️  No positions found for this user.\n")
        return
    print("\n📊 Player positions:\n" + "="*80)
    for idx, pos in enumerate(positions, 1):
        print(f"🔹 Position #{idx}:")
        print(f"   🏷️  Market: {pos.get('title', 'N/A')} ({pos.get('slug', '-')})")
        print(f"   ➡️  Outcome: {pos.get('outcome', 'N/A')}")
        print(f"   📈 Size: {pos.get('size', 0):,.4f}")
        print(f"   💵 Initial value:  {pos.get('initialValue', 0):,.2f}")
        print(f"   📊 Current value:  {pos.get('currentValue', 0):,.2f}")
        print(f"   ℹ️  PnL:           {pos.get('cashPnl', 0):,.2f} USDC ({pos.get('percentPnl', 0):.2f}%)")
        print(f"   🔗 Asset ID:       {pos.get('asset', 'N/A')}")
        print(f"   📅 Expiration date: {pos.get('endDate', 'N/A')}")
        print("-"*80)
    print()

def detect_big_positions(positions: list, size_limit: float = 1000.0):
    """Returns a list of positions above the defined limit."""
    big_positions = []
    for position in positions:
        if position.get('initialValue', 0) > size_limit:
            big_positions.append(position)
    return big_positions

if __name__ == '__main__':
    # Example usage - replace with actual wallet address
    user = input("Enter user address to fetch positions: ") or config.TRADER_WALLET
    positions = fetch_player_positions(user_address=user)
    if positions:
        print("positions", positions[0])
        insert_player_positions_batch(positions)
        print_positions_readable(positions)
    else:
        print("No positions found for this user.")

