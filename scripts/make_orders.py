from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
from config import get_config

# Load configuration once at module level
config = get_config()

# Initialize client once and reuse across all orders
_client = None

def _get_client() -> ClobClient:
    global _client
    if _client is None:
        _client = ClobClient(
            config.CLOB_API_URL,
            key=config.PRIVATE_KEY,
            chain_id=config.POLY_CHAIN_ID,
            signature_type=1,
            funder=config.POLY_FUNDER,
        )
        _client.set_api_creds(_client.create_or_derive_api_creds())
    return _client

def make_order(price: float, size: float, side: str, token_id: str):
    try:
        print('Making order...')
        client = _get_client()

        order_args = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id,
        )
        signed_order = client.create_order(order_args)
        resp = client.post_order(signed_order, OrderType.GTC)
        print(resp)
        return resp
    except Exception as e:
        print(f"Error making order: {e}")
        return None

if __name__ == "__main__":
    make_order(price=0.071, size=14.1, side=BUY, token_id='27745789011483877770092220164639878505910623464021791529418856008078952259643')
