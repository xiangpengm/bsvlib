from typing import List, Optional

from ..constants import Chain
from ..keys import PrivateKey
from ..script.script import Script
from ..script.type import ScriptType, P2pkhScriptType, UnknownScriptType
from ..service.provider import Provider
from ..service.service import Service


class Unspent:

    def __init__(self, **kwargs):
        """
        if script type is P2PKH, then set either private key or oddress is enought
        otherwise, then essential to set both locking script and script type
        """
        self.txid: str = kwargs.get('txid')
        self.vout: int = int(kwargs.get('vout'))
        self.satoshi: int = int(kwargs.get('satoshi'))
        self.height: int = -1 if kwargs.get('height') is None else kwargs.get('height')
        self.confirmation: int = 0 if kwargs.get('confirmation') is None else kwargs.get('confirmation')
        # check if set private keys, P2PKH and P2PK only needs one key, but other script types may need more
        self.private_keys: List[PrivateKey] = kwargs.get('private_keys') if kwargs.get('private_keys') else []
        # if address is not set then try to parse from private keys, otherwise check address only
        self.address: str = kwargs.get('address') or (self.private_keys[0].address() if self.private_keys else None)
        # address is good when either address or private keys is set
        # if script type is not set then check address, otherwise check script type only
        self.script_type: ScriptType = kwargs.get('script_type') or (P2pkhScriptType() if self.address else UnknownScriptType())
        # if locking script is not set then parse from address, otherwise check locking script only
        self.locking_script: Script = kwargs.get('locking_script') or (P2pkhScriptType.locking(self.address) if self.address else None)
        # validate
        assert self.txid and self.vout is not None and self.satoshi is not None and self.locking_script, f'bad unspent'

    def __repr__(self) -> str:
        return f'<Unspent outpoint={self.txid}:{self.vout} satoshi={self.satoshi} script={self.locking_script}>'

    @staticmethod
    def get_unspents(chain: Chain = Chain.MAIN, provider: Optional[Provider] = None, **kwargs) -> List['Unspent']:
        private_keys: List[PrivateKey] = kwargs.get('private_keys') or []
        address: Optional[str] = kwargs.get('address') or (private_keys[0].address() if private_keys else None)
        unspents_map = Service(chain, provider).get_unspents(address=address, **kwargs)
        return [Unspent(**unspent_map) for unspent_map in unspents_map]
