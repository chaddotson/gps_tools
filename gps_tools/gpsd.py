from datetime import datetime
from dateutil.parser import parse
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE
from logging import getLogger
from pytz import utc


logger = getLogger(__name__)


def initialize_gpsd_session(host='localhost', port=2947):
    # Listen on port 2947 (gpsd) of localhost

    logger.info("Initializing GPSd: Host: %s, Port: %d", host, port)

    session = gps(host, str(port))
    session.stream(WATCH_ENABLE | WATCH_NEWSTYLE)

    # spool up session ======================
    session.next()
    session.next()
    session.next()
    session.next()
    # spool up session ======================

    logger.info("GPSd session initilized.")

    return session


def convert_session_fix_to_seconds_since_epoch(fix_time):

    logger.debug("Converting time string from gps to seconds since epoch")

    epoch = datetime(1970, 1, 1, 0, 0, tzinfo=utc)

    gps_datetime = parse(fix_time) if fix_time is not None else epoch

    diff = (gps_datetime - epoch)

    return diff.total_seconds() + diff.microseconds / 1000000


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

    gps_time = session.fix.time

    if not isinstance(gps_time, float):
        gps_time = convert_session_fix_to_seconds_since_epoch(gps_time)

    return {
        'time': gps_time,
        "latitude": session.fix.latitude,
        "longitude": session.fix.longitude,
        "alitude": session.fix.altitude,
        "speed": session.fix.speed,
        "longitudeError": session.fix.epx,
        "latitudeError": session.fix.epy,
        "altitudeError": session.fix.epv,
        "timeOffset": session.fix.ept,
        "speedError": session.fix.eps,
        "track": session.fix.track,
        "climb": session.fix.climb,
        "satellites": satellites
    }
