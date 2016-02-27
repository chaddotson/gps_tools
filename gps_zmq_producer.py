from argparse import ArgumentParser

from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE
from time import sleep

import zmq

from logging import basicConfig, getLogger, INFO, DEBUG

logger = getLogger(__name__)


def get_args():
    parser = ArgumentParser(description='GPSd client / ZMQ PUSH producer for GPS info.')
    parser.add_argument('--zmq_interface', default='*', help='interface to operate on.  default=*')
    parser.add_argument('--zmq_port', default=32000, help='interface to operate on.  default=32000')

    parser.add_argument('--gpsd_host', default="localhost", help='Host for gpsd.  default=localhost')
    parser.add_argument('--gpsd_port', default=2947, help='Port for gpsd.  default=2947')

    parser.add_argument('--rate', default=1/5, help='Rate to push GPS updates. default=0.2hz')
    parser.add_argument('-v', '--verbose', help='Verbose log output', default=False, action='store_true')
    return parser.parse_args()


def initialize_gpsd_session(host, port):
    # Listen on port 2947 (gpsd) of localhost
    session = gps(host, str(port))
    session.stream(WATCH_ENABLE | WATCH_NEWSTYLE)

    # spool up session ======================
    session.next()
    session.next()
    session.next()
    session.next()
    # spool up session ======================

    return session


def initialize_zmq_socket(interface, port):
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://{0}:{1}".format(interface, port))
    return zmq_socket


def convert_gps_session_to_json(session):

    satellites = []

    for satellite in session.satellites:
        satellites.append({
            "prn": satellite.PRN,
            "azimuth": satellite.azimuth,
            "elevation": satellite.elevation,
            "ss": satellite.ss,
            "used": satellite.used
        })

    return {
        'time': session.data.get("time", None),
        "latitude": session.data.get("lat", None),
        "longitude": session.data.get("lon", None),
        "alitude": session.data.get("alt", None),
        "speed": session.data.get("speed", None),
        "longitudeError": session.data.get("epx", None),
        "latitudeError": session.data.get("epy", None),
        "altitudeError": session.data.get("epv", None),
        "timeOffset": session.data.get("ept", None),
        "speedError": session.data.get("eps", None),
        "track": session.data.get("track", None),
        "climb": session.data.get("climb", None),
        "satellites": satellites
    }


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

        try:
            zmq_socket.send_json(convert_gps_session_to_json(session))
        except zmq.error.Again:
            pass

        sleep(time_to_sleep)


if(__name__ == "__main__"):
    main()
