from argparse import ArgumentParser
from logging import basicConfig, getLogger, INFO, DEBUG

from zmq import Context, PULL

logger = getLogger(__name__)


def get_args():
    parser = ArgumentParser(description='ZMQ PULL consumer for GPS info.')
    parser.add_argument('zmq_host', help='ZMQ host to recv pull messages from.')
    parser.add_argument('--zmq_port', type=int, default=32000, help='ZMQ port to connect on.  default=32000')

    parser.add_argument('-v', '--verbose', help='Verbose log output', default=False, action='store_true')
    return parser.parse_args()


def initialize_zmq_socket(host, port):
    logger.info("Initializing ZMQ consumer socket: Host: %s, Port: %d", host, port)
    context = Context()
    zmq_socket = context.socket(PULL)
    zmq_socket.connect("tcp://{0}:{1}".format(host, port))
    logger.info("ZMQ consumer socker initilized.")
    return zmq_socket


def main():
    basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    args = get_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    zmq_socket = initialize_zmq_socket(args.zmq_host, args.zmq_port)

    while True:
        work = zmq_socket.recv_json()
        print work


if(__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
        pass
