# TransferTracker
Using Python 3 + Web3.py.

First you want to edit run.py and utilize the callback function for whatever you want. Currently it just outputs all the transfers.

This isn't production ready as there is serious lag when using a node with SSL. Direct connections are amazing tho.
To run the program
```
  chmod +x ./run.py
```

```
usage: run.py [-h] [--daemon {start,stop,restart}] [--stderr STDERR] [--stdout STDOUT] [--stdin STDIN] [--ethnode ETHNODE] [--from-block FROM_BLOCK] [--loglevel {DEBUG,INFO,WARNING,ERROR}]

Track ERC721 and ERC1155 transfers on an EVM compatible blockchain

options:
  -h, --help            show this help message and exit
  --daemon {start,stop,restart}, -d {start,stop,restart}
                        Run as a daemon
  --stderr STDERR       Daemon stderr file
  --stdout STDOUT       Daemon stdout file
  --stdin STDIN         Daemon stdin file
  --ethnode ETHNODE     Ethereum node to connect to
  --from-block FROM_BLOCK
                        Block number to start from
  --loglevel {DEBUG,INFO,WARNING,ERROR}, -l {DEBUG,INFO,WARNING,ERROR}
                        Set the log level (DEBUG, INFO, WARNING, ERROR). Default is INFO.
```
