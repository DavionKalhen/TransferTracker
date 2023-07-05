import logging
import os

from time import time
from argparse import ArgumentParser
from deps.daemon import Daemon
from dotenv import load_dotenv
from web3 import Web3
from tokenTrackers.ERC721TransferTracker import ERC721TransferTracker
from tokenTrackers.ERC1155TransferTracker import ERC1155TransferTracker

load_dotenv()

erc721Tracker = ERC721TransferTracker()
erc1155Tracker = ERC1155TransferTracker()

web3 = None

trackedERCEvents = {
    erc721Tracker.event_keccak: erc721Tracker,
    erc1155Tracker.event_keccak: erc1155Tracker
}

useless_functions = [
    '0x',
    '0x610737cb',
    '0xa22cb465',
    '0x2e1a7d4d',
    '0x095ea7b3',
    '0x3593564c',
]

def process_event(log, value, processed):
    if log.topics[0].hex() in trackedERCEvents:
        logging.debug("Found ERC Event: %s(%s)" % (
            trackedERCEvents[log.topics[0].hex()].event_keccak, log.address))

        item = trackedERCEvents[log.topics[0].hex()].process_event(
            web3, log, value)
        if item:
            processed.append(item)

def scan_for_erc_transfer_events(block, callback):
    logging.info(f"Processing {len(block.transactions)} transactions")
    processed = []

    for tx_hash in block.transactions:
        tx = web3.eth.get_transaction(tx_hash)
        if tx.gas == 21000 or tx.input[:10] in useless_functions:
            continue
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
        value = tx.value / 10 ** 18
        for log in tx_receipt.logs:
            process_event(log, value, processed)
    callback(processed)


def handle_new_block(block, callback):
    logging.info(f"\n\nNew block mined - Block number: {block.number}")
    start = time()
    scan_for_erc_transfer_events(block, callback)
    end = time()
    logging.info(f"Processed block in {end - start} seconds")
    with open(".block_height", "w") as fn:
        fn.write(str(block.number))


def process_localdir_for_fork(pwd, arg):
    if(arg.startswith('./')):
        return pwd + arg[1:]
    elif(not arg.startswith('/')):
        return pwd + os.sep + arg
    return arg


def catch_up_to_current_block(last_block, callback):
    current_block_number = web3.eth.block_number
    if current_block_number == last_block.number:
        return current_block_number
    block = web3.eth.get_block(last_block.number + 1)
    handle_new_block(block, callback)
    return catch_up_to_current_block(block, callback)


def main(*args, **kwargs):
    latest_block_processed = None
    kwargs = kwargs['kwargs']
    callback = kwargs['callback']
    if 'from_block' in kwargs and kwargs['from_block'] != 'latest':
        from_block = kwargs['from_block']
        current_block = web3.eth.block_number
        logging.info(
            f"Playing Catchup starting at block {from_block}. Current block is {current_block}")
        block = web3.eth.get_block(from_block, True)
        latest_block_processed = catch_up_to_current_block(block, callback)

    block_filter = web3.eth.filter('latest')
    tracking = []
    if erc721Tracker.erc20Tracker.track == True:
        tracking.append("ERC20")
    if erc721Tracker.track == True:
        tracking.append("ERC721")
    if erc1155Tracker.track == True:
        tracking.append("ERC1155")


    logging.info("Starting Transfer Tracker: %s" % ", ".join(tracking))

    while True:
        entries = block_filter.get_new_entries()
        if entries:
            for entry in entries:
                block = web3.eth.get_block(entry.hex(), True)

                if block.number < latest_block_processed:
                    logging.error(
                        "Block number is less than latest block processed. This should never happen.")
                    exit(1)

                if block.number == latest_block_processed:
                    continue

                if latest_block_processed + 1 != block.number:
                    for i in range(latest_block_processed + 1, block.number-1):
                        block = web3.eth.get_block(i, True)
                        handle_new_block(block, callback)

                handle_new_block(block, callback)


def process_daemon(args, **kwargs):
    pwd = os.path.dirname(os.path.realpath(__file__))
    stderr = process_localdir_for_fork(pwd, str(args.stderr))
    stdout = process_localdir_for_fork(pwd, str(args.stdout))
    stdin = process_localdir_for_fork(pwd, str(args.stdin))

    dmn = Daemon(pidfile=pwd + os.sep + '.pid',
                 stderr=stderr, stdout=stdout, stdin=stdin)

    if args.daemon == 'start':
        logging.info("[\033[1;32m***\033[0m] Starting daemon")
        try:
            dmn.start(main, args=(), kwargs={})
        except Daemon.PIDFileAlreadyExist:
            logging.error("[\033[1;31m***\033[0m] Daemon already running")
    elif args.daemon == 'stop':
        logging.info("[\033[1;32m***\033[0m] Stopping daemon")
        try:
            dmn.stop()
            logging.info("[\033[1;32m***\033[0m] Daemon stopped")

        except Daemon.PIDFileDoesNotExist:
            logging.error("[\033[1;31m***\033[0m] Daemon not running")
    elif args.daemon == 'restart':
        logging.info("[\033[1;32m***\033[0m] Restarting daemon")
        try:
            dmn.restart(main, args=(), kwargs=kwargs)
        except Daemon.PIDFileDoesNotExist:
            logging.error("[\033[1;31m***\033[0m] Daemon not running")


def initialize_cli():
    block_height = 'latest'
    if os.path.exists(".block_height"):
        with open(".block_height", "r") as fn:
            block_height = int(fn.read())

    ethnode_default = os.getenv('ETHNODE')
    parser = ArgumentParser(
        description='Track ERC721 and ERC1155 transfers on an EVM compatible blockchain')
    parser.add_argument(
        '--daemon', '-d',  choices=['start', 'stop', 'restart'], help='Run as a daemon')
    parser.add_argument(
        '--stderr', help='Daemon stderr file', default='/dev/null')
    parser.add_argument(
        '--stdout', help='Daemon stdout file', default='/dev/null')
    parser.add_argument('--stdin', help='Daemon stdin file',
                        default='/dev/null')
    parser.add_argument(
        '--ethnode', help='Ethereum node to connect to', default=ethnode_default)
    parser.add_argument(
        '--from-block', help='Block number to start from', default=block_height)
    parser.add_argument('--loglevel', '-l', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO',
                        help='Set the log level (DEBUG, INFO, WARNING, ERROR). Default is INFO.')
    parser.add_argument('--track', choices=[20, 721, 1155], default=[721,1155,20], nargs='*', type=int,
                        help='Track ERC20, ERC721, and/or ERC1155 transfers. Default is all three.')

    args = parser.parse_args()

    if args.track:
        global erc1155Tracker, erc721Tracker
        erc1155Tracker.track = 1155 in args.track
        erc721Tracker.track = 721 in args.track
        erc721Tracker.erc20Tracker.track = 20 in args.track

    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=log_level)
    provider_url = str(args.ethnode)
    global web3
    web3 = Web3(Web3.HTTPProvider(provider_url))
    return args
