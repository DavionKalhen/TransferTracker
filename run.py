#!/bin/python3
import logging
from TransferTracker import main, process_daemon, initialize_cli


def tracker_callback(transfer_events):
    for transfer_event in transfer_events:
        if(transfer_event['standard'] in [721, 1155]):
           logging.info("(%d)%-30s %-42s -> 0x%s (%d) %-4fETH" % (transfer_event['amount'], transfer_event['name'],
                     '0x' + transfer_event['from'], transfer_event['to'], transfer_event['token_id'], transfer_event['value']))
        else:
           amount = transfer_event['amount']
           if transfer_event['decimals'] > 0:
                amount /= transfer_event['decimals']
           logging.info("(%-4f)%-30s %-42s -> 0x%s (%d) %-4fETH" % (amount, transfer_event['name'],
                     '0x' + transfer_event['from'], transfer_event['to'], transfer_event['token_id'], transfer_event['value']))



if __name__ == "__main__":
    args = initialize_cli()

    if args.daemon:
        process_daemon(
            args, kwargs={'from_block': args.from_block, 'callback': tracker_callback})
    else:
        main(kwargs={'from_block': args.from_block,
             'callback': tracker_callback})
