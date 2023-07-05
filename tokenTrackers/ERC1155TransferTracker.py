from abis.erc721abi import genericERC721ABI


class ERC1155TransferTracker:
    event_keccak = '0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62'
    contracts_checked = {}

    def process_event(self, web3, log, value):
        contract = web3.eth.contract(address=log.address, abi=genericERC721ABI)
        if contract.address not in self.contracts_checked:
            try:
                self.contracts_checked[contract.address] = {
                    'supports_erc721': False, 'supports_erc1155': False, 'name': None}
                supports_erc1155 = contract.functions.supportsInterface(
                    '0xd9b67a26').call()
                name = ""
                if supports_erc1155:
                    name = contract.functions.name().call()
                self.contracts_checked[contract.address] = {
                    'supports_erc721': False, 'supports_erc1155': supports_erc1155, 'name': name}
            except:
                return None
        else:
            supports_erc1155 = self.contracts_checked[contract.address]['supports_erc721']
            name = self.contracts_checked[contract.address]['name']

        if supports_erc1155:
            transfer_event = {'name': name}
            operator_address = log.topics[1].hex()[-40:]
            from_address = log.topics[2].hex()[-40:]
            to_address = log.topics[3].hex()[-40:]
            token_id = int(log.data[2:66], 16)
            amount = int(log.data[68:], 16)
            transfer_event['from'] = from_address
            transfer_event['to'] = to_address
            transfer_event['token_id'] = token_id
            transfer_event['value'] = value
            transfer_event['amount'] = amount
            transfer_event['standard'] = 1155
            transfer_event['decimals'] = 0            
            return transfer_event
        return None
