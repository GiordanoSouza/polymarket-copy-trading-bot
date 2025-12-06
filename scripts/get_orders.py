import requests
from datetime import datetime


url = "https://data-api.polymarket.com/activity"

# Example: Get user address from input or environment
user_address = input("Enter user address to fetch activities: ")

resp = requests.get(url, params={
    "user": user_address,
    "limit":"4",
    "sortBy":"TIMESTAMP",
    "sortDirection":"DESC",
})
activity = resp.json()
print(activity)

print("\n" + "="*80)
print(f"TOTAL ACTIVITIES: {len(activity)}")
print("="*80 + "\n")

for i, act in enumerate(activity, 1):
    # Convert timestamp to readable date/time
    act_time = datetime.fromtimestamp(act['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
    
    # Determine activity type and emoji
    if act['type'] == 'TRADE':
        type_emoji = "🟢 BUY" if act['side'] == 'BUY' else "🔴 SELL"
        type_label = f"TRADE - {type_emoji}"
    elif act['type'] == 'YIELD':
        type_label = "💰 YIELD"
    else:
        type_label = f"📋 {act['type']}"
    
    print(f"\n{'─'*80}")
    print(f"ACTIVITY #{i} - {type_label}")
    print(f"{'─'*80}")
    print(f"📅 Date/Time: {act_time}")
    
    # Display specific information for TRADE type
    if act['type'] == 'TRADE' and act.get('title'):
        print(f"📊 Market: {act['title']}")
        print(f"🎯 Outcome: {act['outcome']} (Index: {act['outcomeIndex']})")
        print(f"\n💰 OPERATION DETAILS:")
        print(f"   • Quantity: {act['size']:,.2f} tokens")
        print(f"   • Unit Price: ${act['price']:.6f}")
        print(f"   • USDC Value: ${act['usdcSize']:,.2f}")
        print(f"   • Total Value: ${act['size'] * act['price']:,.2f}")
    
    # Display specific information for YIELD type
    elif act['type'] == 'YIELD':
        print(f"\n💵 YIELD DETAILS:")
        print(f"   • Quantity: {act['size']:.6f} tokens")
        print(f"   • USDC Value: ${act['usdcSize']:.6f}")
    
    # Trader information (if available)
    if act.get('name'):
        print(f"\n👤 TRADER:")
        print(f"   • Name: {act['name']}")
        print(f"   • Pseudonym: {act['pseudonym']}")
        if act.get('bio'):
            print(f"   • Bio: {act['bio']}")
    
    # Technical information
    print(f"\n🔗 TECHNICAL INFORMATION:")
    print(f"   • Proxy Wallet: {act['proxyWallet']}")
    print(f"   • TX Hash: {act['transactionHash']}")
    if act.get('eventSlug') and act['eventSlug']:
        print(f"   • Market: https://polymarket.com/event/{act['eventSlug']}")

print(f"\n{'='*80}")
print("END OF ACTIVITIES")
print("="*80 + "\n")