from http import client
from algosdk.v2client import algod, indexer

from resolver import ans_resolver

def SetupClient():
    api_key = "iG4m46pAcU5ws8WYhgYPu1rywUbfYT2DaAfSs9Tv"
    
    # Purestake conn
    algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
    headers = {
    "X-API-Key": api_key
    }
    
    algod_client=algod.AlgodClient(api_key, algod_address, headers=headers)
    return algod_client

def SetupIndexer():
    api_key = "iG4m46pAcU5ws8WYhgYPu1rywUbfYT2DaAfSs9Tv"
   
    algod_address = "https://mainnet-algorand.api.purestake.io/idx2"
    headers = {
        'X-API-key' : api_key,
    }
    algod_indexer=indexer.IndexerClient("", algod_address, headers)
    
    return algod_indexer

client = SetupClient()
indexer = SetupIndexer()
resolver_obj = ans_resolver(client, indexer)
print(resolver_obj.resolve_name('rand'))
print(resolver_obj.get_names_owned_by_address('RANDGVRRYGVKI3WSDG6OGTZQ7MHDLIN5RYKJBABL46K5RQVHUFV3NY5DUE'))
