from bsvlib import Wallet, Transaction, TxInput, Key
from bsvlib.constants import SIGHASH
from bsvlib.service import WhatsOnChain

provider = WhatsOnChain()
private_key = Key('L5agPjZKceSTkhqZF2dmFptT5LFrbr6ZGPvP7u4A6dvhTrr71WZ9')
unspents = Wallet([private_key], provider=provider).get_unspents(refresh=True)

t = Transaction(provider=provider)
t.add_input(TxInput(unspents[0], sighash=SIGHASH.NONE_ANYONECANPAY_FORKID))
t.sign()

unlocking_script = t.tx_inputs[0].unlocking_script.hex()

# it's good to add more inputs here
t.add_inputs(unspents[1:])
# function sign will ONLY sign inputs which unlocking script is empty
# because the first input was signed before, so it will NOT be re-signed this time
t.add_change().sign()

# ensure that we didn't re-sign the first input
assert t.tx_inputs[0].unlocking_script.hex() == unlocking_script

print(t.broadcast())
