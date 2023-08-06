from algosdk.v2client import algod, indexer

from resolver import ans_resolver

def SetupClient(network):

    if(network=="sandbox"):
        # Local sandbox node 
        algod_address = "http://localhost:4001"
        algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    elif(network=="purestake"):
        # Purestake conn
        algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
        algod_token = "iG4m46pAcU5ws8WYhgYPu1rywUbfYT2DaAfSs9Tv"
        headers = {
        "X-API-Key": algod_token,
        }
    
    else:
        raise ValueError

    algod_client=algod.AlgodClient(algod_token, algod_address, headers=headers)
    return algod_client

def SetupIndexer(network):
    if(network=="purestake"):
        algod_address = "https://mainnet-algorand.api.purestake.io/idx2"
        headers = {
            'X-API-key' : 'iG4m46pAcU5ws8WYhgYPu1rywUbfYT2DaAfSs9Tv',
        }
        algod_indexer=indexer.IndexerClient("", algod_address, headers)
    
    return algod_indexer

client = SetupClient("purestake")    
indexer = SetupIndexer("purestake")

resolver_obj = ans_resolver(client, indexer)
print(resolver_obj.resolve_name('rand.algo'))
print(resolver_obj.get_names_owned_by_address('RANDGVRRYGVKI3WSDG6OGTZQ7MHDLIN5RYKJBABL46K5RQVHUFV3NY5DUE'))
