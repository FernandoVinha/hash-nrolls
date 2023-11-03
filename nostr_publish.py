import json
import ssl
import time
import uuid
from pynostr.event import Event
from pynostr.relay_manager import RelayManager
from pynostr.filters import FiltersList, Filters
from pynostr.message_type import ClientMessageType
from pynostr.key import PrivateKey
import requests

def get_actual_block():
    url = "https://api.blockchair.com/bitcoin/stats"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['blocks']
    else:
        print(f"Erro ao consultar a API. Status Code: {response.status_code}")
        return None
    
def Publish_in_nostr(invoice=None):
    relay_manager = RelayManager(timeout=6)
    relay_manager.add_relay("wss://relay.nostrss.re")
    relay_manager.add_relay("wss://nostr.bitcoiner.social")
    relay_manager.add_relay("wss://relay.nostr.bg")
    relay_manager.add_relay("wss://relay.damus.io")
    relay_manager.add_relay("wss://nostr.mom")
    relay_manager.add_relay("wss://nostr-pub.wellorder.net")
    #private_key = PrivateKey()
    private_key = PrivateKey.from_nsec('nsec1t5rs7rjp9t2gdm2v59wr6v5c3038tfyfycdtlr4hcryd9jqeg4ps44cuum')
    #print(private_key)

    public_key = private_key.public_key
    #print(f"Private key: {private_key.bech32()}")
    #print(f"Public key: {public_key.bech32()}")

    filters = FiltersList([Filters(authors=[private_key.public_key.hex()], limit=100)])
    subscription_id = uuid.uuid1().hex
    relay_manager.add_subscription_on_all_relays(subscription_id, filters)

    bloco_atual = get_actual_block()
    event = Event("No Bloco " + str(bloco_atual) + " acabamos de vender mais uma cerveja na Hash'n Roll durante a SatsConf! \nInvoice Payment: " + str(invoice) )
    event.sign(private_key.hex())

    relay_manager.publish_event(event)
    relay_manager.run_sync()
    time.sleep(5) # allow the messages to send
    while relay_manager.message_pool.has_ok_notices():
        ok_msg = relay_manager.message_pool.get_ok_notice()
        #print(ok_msg)
    while relay_manager.message_pool.has_events():
        event_msg = relay_manager.message_pool.get_event()
        #print(event_msg.event.to_dict())
    
    print('nostr msg sended!')
    #return()


