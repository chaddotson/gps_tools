from argparse import ArgumentParser
from dateutil.parser import parse
from json import dumps
from logging import basicConfig, getLogger, INFO, DEBUG
from time import sleep

from redis import StrictRedis

from gps_tools.gpsd import GPSDSession




logger = getLogger(__name__)


def get_args():
    parser = ArgumentParser(description='GPSd client / Redis producer for GPS info.')
    # parser.add_argument('--zmq_interface', default='*', help='interface to operate on.  default=*')
    # parser.add_argument('--zmq_port', type=int, default=32000, help='interface to operate on.  default=32000')

    parser.add_argument('--gpsd_host', default="localhost", help='Host for gpsd.  default=localhost')
    parser.add_argument('--gpsd_port', default=2947, help='Port for gpsd.  default=2947')

    parser.add_argument('--rate', type=float, default=0.5, help='Rate to push GPS updates. default=0.5hz')
    parser.add_argument('-v', '--verbose', help='Verbose log output', default=False, action='store_true')
    return parser.parse_args()

def main():
    basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    args = get_args()

    if args.verbose:
        getLogger('').setLevel(DEBUG)

    redis = StrictRedis(host='riker')

    time_to_sleep = 1/args.rate


    session = GPSDSession(args.gpsd_host, args.gpsd_port)

    while(True):
        gps_info = session.get_gps_info()

        logger.debug("Pushing GPS data.")

        redis.set("GPS", dumps(gps_info))

        sleep(time_to_sleep)


if(__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
        pass
