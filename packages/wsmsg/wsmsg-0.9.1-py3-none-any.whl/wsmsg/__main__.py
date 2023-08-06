from argparse import ArgumentParser

import logging
from .server import Server

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('--key', '-k', type=str, default='abc123')
    parser.add_argument('--host', '-H', type=str, default='0.0.0.0')
    parser.add_argument('--port', '-p', type=int, default=1234)
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--stats', '-s', action='store_true')
    parser.add_argument('--debug', '-D', action='store_true')
    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    if not args.quiet:
        logging.basicConfig()
        logging.getLogger(__package__).setLevel(level)

    Server(args.host, args.port, args.key, args.stats).run()
    # server = ServerThread(args.host, args.port, args.key, args.debug)
    # server.start()
    # def cleanup():
    #     server.stop()
    #     server.join()
    # atexit.register(cleanup)
    # while True:
    #     time.sleep(10)
