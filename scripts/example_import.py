"""
Exemplo de uso do script de importação de histórico de players do Polymarket

Execute este arquivo para importar o histórico de um ou mais players
"""

from import_player_history import import_player_history, import_multiple_players

# ============================================================
# OPÇÃO 1: Importar um único player
# ============================================================

def import_single_player():
    """Importa o histórico de um único player"""
    
    # Endereço da carteira do player
    player_address = "0xf2f6af4f27ec2dcf4072095ab804016e14cd5817"
    
    # Importar histórico dos últimos 365 dias (1 ano)
    import_player_history(player_address, days_back=7)


# ============================================================
# OPÇÃO 2: Importar múltiplos players
# ============================================================

def import_multiple():
    """Importa o histórico de múltiplos players"""
    
    # Lista de endereços de players
    players = [
        "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b",  # Player 1
        # Adicione mais players aqui:
        # "0x1234567890abcdef1234567890abcdef12345678",  # Player 2
        # "0xabcdef1234567890abcdef1234567890abcdef12",  # Player 3
    ]
    
    # Importar histórico de todos os players
    import_multiple_players(players, days_back=365)


# ============================================================
# OPÇÃO 3: Importar histórico recente (última semana)
# ============================================================

def import_recent_activity():
    """Importa apenas atividades recentes (útil para atualizações diárias)"""
    
    player_address = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
    
    # Importar apenas últimos 7 dias
    import_player_history(player_address, days_back=7)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    # Escolha qual função executar:
    
    # Para um único player (1 ano):
    import_single_player()
    
    # Para múltiplos players (descomente para usar):
    # import_multiple()
    
    # Para atualização recente (descomente para usar):
    # import_recent_activity()

