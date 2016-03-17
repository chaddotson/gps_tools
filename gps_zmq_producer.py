#!/usr/bin/env python

from argparse import ArgumentParser
from logging import basicConfig, getLogger, INFO, DEBUG
from time import sleep
from zmq import Context, PUSH
from zmq.error import Again as NoClientsTimeoutError

from gps_tools.gpsd import initialize_gpsd_session, convert_gps_session_to_json

logger = getLogger(__name__)


def get_args():
    parser = ArgumentParser(description='GPSd client / ZMQ PUSH producer for GPS info.')
    parser.add_argument('--zmq_interface', default='*', help='interface to operate on.  default=*')
    parser.add_argument('--zmq_port', type=int, default=32000, help='interface to operate on.  default=32000')

    parser.add_argument('--gpsd_host', default="localhost", help='Host for gpsd.  default=localhost')
    parser.add_argument('--gpsd_port', default=2947, help='Port for gpsd.  default=2947')

    parser.add_argument('--rate', type=float, default=0.5, help='Rate to push GPS updates. default=0.5hz')
    parser.add_argument('-v', '--verbose', help='Verbose log output', default=False, action='store_true')
    return parser.parse_args()


def initialize_zmq_socket(interface, port):
    logger.info("Initializing ZMQ producer socket: Host: %s, Port: %d", interface, port)

    context = Context()
    zmq_socket = context.socket(PUSH)
    zmq_socket.bind("tcp://{0}:{1}".format(interface, port))

    logger.info("ZMQ producer socker initilized.")
    return zmq_socket


def main():
    basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    args = get_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    time_to_sleep = 1/args.rate

    zmq_socket = initialize_zmq_socket(args.zmq_interface, args.zmq_port)
    session = initialize_gpsd_session(args.gpsd_host, args.gpsd_port)

    while(True):
        report = session.next()

        logger.debug("Pushing GPS data.")

        try:
            zmq_socket.send_json(convert_gps_session_to_json(session))
        except NoClientsTimeoutError:
            pass

        sleep(time_to_sleep)


if(__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
        pass
