import requests
from datetime import datetime


url = "https://data-api.polymarket.com/activity"
resp = requests.get(url, params={
    "user":"0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",
    "limit":"1",
    "sortBy":"TIMESTAMP",
    "sortDirection":"DESC",
})
activity = resp.json()
print(activity)

print("\n" + "="*80)
print(f"TOTAL DE ATIVIDADES: {len(activity)}")
print("="*80 + "\n")

for i, act in enumerate(activity, 1):
    # Converter timestamp para data/hora legível
    act_time = datetime.fromtimestamp(act['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
    
    # Determinar tipo de atividade e emoji
    if act['type'] == 'TRADE':
        type_emoji = "🟢 COMPRA" if act['side'] == 'BUY' else "🔴 VENDA"
        type_label = f"TRADE - {type_emoji}"
    elif act['type'] == 'YIELD':
        type_label = "💰 RENDIMENTO (YIELD)"
    else:
        type_label = f"📋 {act['type']}"
    
    print(f"\n{'─'*80}")
    print(f"ATIVIDADE #{i} - {type_label}")
    print(f"{'─'*80}")
    print(f"📅 Data/Hora: {act_time}")
    
    # Exibir informações específicas do tipo TRADE
    if act['type'] == 'TRADE' and act.get('title'):
        print(f"📊 Mercado: {act['title']}")
        print(f"🎯 Resultado: {act['outcome']} (Index: {act['outcomeIndex']})")
        print(f"\n💰 DETALHES DA OPERAÇÃO:")
        print(f"   • Quantidade: {act['size']:,.2f} tokens")
        print(f"   • Preço Unitário: ${act['price']:.6f}")
        print(f"   • Valor em USDC: ${act['usdcSize']:,.2f}")
        print(f"   • Valor Total: ${act['size'] * act['price']:,.2f}")
    
    # Exibir informações específicas do tipo YIELD
    elif act['type'] == 'YIELD':
        print(f"\n💵 DETALHES DO RENDIMENTO:")
        print(f"   • Quantidade: {act['size']:.6f} tokens")
        print(f"   • Valor em USDC: ${act['usdcSize']:.6f}")
    
    # Informações do trader (se disponível)
    if act.get('name'):
        print(f"\n👤 TRADER:")
        print(f"   • Nome: {act['name']}")
        print(f"   • Pseudônimo: {act['pseudonym']}")
        if act.get('bio'):
            print(f"   • Bio: {act['bio']}")
    
    # Informações técnicas
    print(f"\n🔗 INFORMAÇÕES TÉCNICAS:")
    print(f"   • Proxy Wallet: {act['proxyWallet']}")
    print(f"   • TX Hash: {act['transactionHash']}")
    if act.get('eventSlug') and act['eventSlug']:
        print(f"   • Market: https://polymarket.com/event/{act['eventSlug']}")

print(f"\n{'='*80}")
print("FIM DAS ATIVIDADES")
print("="*80 + "\n")