from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
import os
from dotenv import load_dotenv

def make_order(price: float, size: float, side: str, token_id: str):
    load_dotenv()
    try:
        print('Making order...')
        host: str = os.getenv("CLOB_API_URL")
        key: str = os.getenv("PK") #This is your Private Key. Export from https://reveal.magic.link/polymarket or from your Web3 Extension
        chain_id: int = int(os.getenv("POLY_CHAIN_ID")) #No need to adjust this
        POLYMARKET_PROXY_ADDRESS: str = os.getenv("POLY_FUNDER") #This is the address listed below your profile picture when using the Polymarket site.

        ### Initialization of a client using a Polymarket Proxy associated with an Email/Magic account. If you login with your email use this example.
        client = ClobClient(host, key=key, chain_id=chain_id, signature_type=1, funder=POLYMARKET_PROXY_ADDRESS)

        ## Create and sign a limit order buying 5 tokens for 0.010c each
        #Refer to the API documentation to locate a tokenID: https://docs.polymarket.com/developers/gamma-markets-api/fetch-markets-guide
        client.set_api_creds(client.create_or_derive_api_creds()) 

        order_args = OrderArgs(
        price=price,
        size=size,
        side=side,
        token_id=token_id,
        )
        signed_order = client.create_order(order_args)
        ## GTC(Good-Till-Cancelled) Order
        resp = client.post_order(signed_order, OrderType.GTC)
        print(resp)
        return resp
    except Exception as e:
        print(f"Error making order: {e}")
        return None

if __name__ == "__main__":
    make_order(price=0.015, size=5.0, side=SELL, token_id='70663352401606372246362604193214664065595751757222752105245221905399175050480')

    