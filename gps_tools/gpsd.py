from datetime import datetime
from dateutil.parser import parse
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE
from logging import getLogger
from pytz import utc


logger = getLogger(__name__)


class GPSDSession(object):
    def __init__(self, host, port):
        self._session = None
        self._initialize_gpsd_session(host, port)

    def _initialize_gpsd_session(self, host, port):
        # Listen on port 2947 (gpsd) of localhost

        logger.info("Initializing GPSd: Host: %s, Port: %d", host, port)

        self._session = gps(host, str(port))
        self._session.stream(WATCH_ENABLE | WATCH_NEWSTYLE)

        # spool up session ======================
        self._session.next()
        self._session.next()
        self._session.next()
        self._session.next()
        # spool up session ======================

        logger.info("GPSd session initilized.")

    def get_gps_info(self):
        self._session.next()

        satellites = []

        for satellite in self._session.satellites:
            satellites.append({
                "prn": satellite.PRN,
                "azimuth": satellite.azimuth,
                "elevation": satellite.elevation,
                "ss": satellite.ss,
                "used": satellite.used
            })


        gps_datetime = self._session.data.get("time", None)

        logger.info(gps_datetime)

        epoch = datetime(1970, 1, 1, 0, 0, tzinfo=utc)


        gps_datetime = parse(gps_datetime) if gps_datetime is not None else epoch

        #logger.info("datetime=%s\nepoch=%s", gps_datetime, epoch)


        diff = (gps_datetime - epoch)
        logger.info(diff.microseconds)

        gps_seconds_since_epoch = diff.total_seconds() + diff.microseconds / 1000000

        return {
            'time': gps_seconds_since_epoch,
            "latitude": self._session.data.get("lat", 0),
            "longitude": self._session.data.get("lon", 0),
            "alitude": self._session.data.get("alt", 0),
            "speed": self._session.data.get("speed", 0),
            "longitudeError": self._session.data.get("epx", 0),
            "latitudeError": self._session.data.get("epy", 0),
            "altitudeError": self._session.data.get("epv", 0),
            "timeOffset": self._session.data.get("ept", 0),
            "speedError": self._session.data.get("eps", 0),
            "track": self._session.data.get("track", 0),
            "climb": self._session.data.get("climb", 0),
            "satellites": satellites
        }
