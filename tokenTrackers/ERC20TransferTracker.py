from abis.erc20abi import genericERC20ABI


class ERC20TransferTracker:
    event_keccak = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
    contracts_checked = {}

    def process_event(self, web3, log, value):
        contract = web3.eth.contract(address=log.address, abi=genericERC20ABI)
        if contract.address not in self.contracts_checked:
            try:
                self.contracts_checked[contract.address] = {
                    'supports_erc20': False, 'supports_erc721': False, 'supports_erc1155': False, 'name': None}
                decimals = contract.functions.decimals().call()
                name = ""
                if decimals > 0:
                    name = contract.functions.name().call()
                supports_erc20 = True
                self.contracts_checked[contract.address] = {
                    'supports_erc721': False, 'supports_erc1155': False, 'supports_erc20': True, 'name': name, 'decimals': decimals}
            except:
                return None
        else:
            supports_erc20 = self.contracts_checked[contract.address]['supports_erc20']
            name = self.contracts_checked[contract.address]['name']
            decimals = self.contracts_checked[contract.address]['decimals']

        if supports_erc20:
            transfer_event = {'name': name}
            from_address = log.topics[1].hex()[-40:]
            to_address = log.topics[2].hex()[-40:]
            try:
                amount = int(log.topics[3].hex(), 16)
            except IndexError:
                amount = int(log.data[2:66], 16)
            transfer_event['from'] = from_address
            transfer_event['to'] = to_address
            transfer_event['token_id'] = 0
            transfer_event['value'] = value
            transfer_event['amount'] = amount
            transfer_event['standard'] = 20
            transfer_event['decimals'] = decimals
            return transfer_event
        return None
