from abis.erc721abi import genericERC721ABI
from tokenTrackers.ERC20TransferTracker import ERC20TransferTracker


class ERC721TransferTracker:
    event_keccak = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
    contracts_checked = {}
    erc20Tracker = ERC20TransferTracker()
    track = True
    def process_event(self, web3, log, value):
        contract = web3.eth.contract(address=log.address, abi=genericERC721ABI)
        if contract.address not in self.contracts_checked:
            try:
                if not self.track: raise Exception()
                self.contracts_checked[contract.address] = {
                    'supports_erc721': False, 'supports_erc1155': False, 'name': None}
                supports_erc721 = contract.functions.supportsInterface(
                    '0x80ac58cd').call()
                name = ""
                if supports_erc721:
                    name = contract.functions.name().call()
                self.contracts_checked[contract.address] = {
                    'supports_erc721': supports_erc721, 'supports_erc1155': False, 'name': name}
            except:
                return self.erc20Tracker.process_event(web3, log, value)
        else:
            supports_erc721 = self.contracts_checked[contract.address]['supports_erc721']
            name = self.contracts_checked[contract.address]['name']

        if supports_erc721:
            transfer_event = {'name': name}
            from_address = log.topics[1].hex()[-40:]
            to_address = log.topics[2].hex()[-40:]
            token_id = int(log.topics[3].hex(), 16)
            transfer_event['from'] = from_address
            transfer_event['to'] = to_address
            transfer_event['token_id'] = token_id
            transfer_event['value'] = value
            transfer_event['amount'] = 1
            transfer_event['standard'] = 721
            transfer_event['decimals'] = 0
            return transfer_event
        return None
