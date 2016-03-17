from argparse import ArgumentParser
from json import dumps
from logging import basicConfig, getLogger, INFO, DEBUG
from time import sleep

from redis import StrictRedis

from gps_tools.gpsd import initialize_gpsd_session, convert_gps_session_to_json

logger = getLogger(__name__)


def get_args():
    parser = ArgumentParser(description='GPSd client / Redis producer for GPS info.')
    parser.add_argument('redis_host', help='Redis host')

    parser.add_argument('--redis_port', default=6379, help='Redis port')
    parser.add_argument('--redis_db', default=0, help='Redis db')
    parser.add_argument('--redis_pw', default=None, help='Redis password')

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

    logger.info("Initializing connection to Redis: Host=%s, Port: %d", args.redis_host, args.redis_port)
    redis = StrictRedis(host=args.redis_host, port=args.redis_port, db=args.redis_db, password=args.redis_pw)

    time_to_sleep = 1/args.rate

    session = initialize_gpsd_session(host=args.gpsd_host, port=args.gpsd_port)

    while(True):
        session.next()

        logger.debug("Pushing GPS data.")

        redis.set("GPS", dumps(convert_gps_session_to_json(session)))

        sleep(time_to_sleep)


if(__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
        pass
