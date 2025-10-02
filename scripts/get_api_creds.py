from py_clob_client.client import ClobClient   
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("CLOB_API_URL")                                   
chain_id = int(os.getenv("POLY_CHAIN_ID", "137"))                 
key = os.getenv("PK")                                 
funder = os.getenv("POLY_FUNDER")                               
sig_type = int(os.getenv("POLY_SIGNATURE_TYPE", "1"))           
                                                                
client = ClobClient(                                            
    host=host,                                                  
    chain_id=chain_id,                                          
    key=key,                                                    
    signature_type=sig_type,                                    
    funder=funder,                                              
)                                                               
                                                                
print("L0 calls:")                                              
print("  ok:", client.get_ok())                                 
print("  server time:", client.get_server_time())               
                                                                
markets = client.get_simplified_markets()                       
print("Sample market:", markets["data"][:1])                    
                                                                
creds = client.create_api_key()
# client.set_api_creds(creds)                 
print("API creds:", creds)                                      
print("Client mode:", client.mode)                