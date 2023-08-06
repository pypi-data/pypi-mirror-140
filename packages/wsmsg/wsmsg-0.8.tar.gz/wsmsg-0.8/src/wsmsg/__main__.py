from argparse import ArgumentParser

from .server import Server

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('--key', type=str, default='abc123')
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=1234)
    parser.add_argument('--stats', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    Server(args.host, args.port, args.key, args.stats, args.debug).run()
    # server = ServerThread(args.host, args.port, args.key, args.debug)
    # server.start()
    # def cleanup():
    #     server.stop()
    #     server.join()
    # atexit.register(cleanup)
    # while True:
    #     time.sleep(10)
