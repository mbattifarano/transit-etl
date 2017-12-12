import logging
from os import listdir
import os.path
from collections import namedtuple
from transit_etl import data_conversion as dc
from transit_etl.models import ApcAvlRecord
from toolz import curry, partition_all, map

FieldSpec = namedtuple('FieldSpec', ('name', 'start', 'length', 'extract'))

fields = [FieldSpec(*data) for data in [
    ('day_of_week', 130, 2, int),
    ('direction', 132, 2, int),
    ('route', 74, 5, int),
    ('trip', 119, 4, str),
    ('block', 87, 6, str),
    ('vehicle_id', 160, 5, int),
    ('year', 72, 2, dc.to_fullyear),
    ('month', 68, 2, int),
    ('day', 70, 2, int),
    ('stop', 0, 5, int),
    ('qstop', 6, 8, dc.trim),  # leading spaces?
    ('name', 15, 33, dc.trim),
    ('arrival_hour', 48, 2, int),
    ('arrival_minute', 50, 2, int),
    ('arrival_second', 52, 2, int),
    ('departure_hour', 264, 2, int),
    ('departure_minute', 266, 2, int),
    ('departure_second', 268, 2, int),
    ('on', 54, 4, int),
    ('off', 58, 4, int),
    ('load', 62, 4, int),
    ('dl_miles', 134, 6, float),
    ('dl_minutes', 140, 5, float),
    ('dl_passenger_miles', 145, 8, float),
    ('dwell_time', 211, 6, float),
    ('gps_delta', 125, 5, int),
    ('scheduled_arrival', 175, 5, str),
    ('schedule_deviation', 204, 7, float),
    ('schedule_traveltime', 180, 6, float),
    ('actual_traveltime', 186, 6, float)
]]

route_name_map = {1: '1', 2: '2', 4: '4', 6: '6', 7: '7', 8: '8', 521: '52L', 11: '11', 12: '12', 13: '13', 14: '14',
                  15: '15', 16: '16', 17: '17', 18: '18', 531: '53L', 20: '20', 21: '21', 22: '22', 24: '24', 26: '26',
                  27: '27', 29: '29', 31: '31', 36: '36', 38: '38', 39: '39', 40: '40', 41: '41', 555: 'P2', 44: '44',
                  48: '48', 51: '51', 53: '53', 54: '54', 55: '55', 56: '56', 57: '57', 58: '58', 59: '59', 60: '60',
                  64: '64', 65: '65', 67: '67', 68: '68', 69: '69', 71: '71', 74: '74', 75: '75', 77: '77', 78: '78',
                  79: '79', 81: '81', 82: '82', 83: '83', 86: '86', 87: '87', 88: '88', 89: '89', 91: '91', 93: '93',
                  611: '61A', 612: '61B', 613: '61C', 614: '61D', 771: 'P71', 666: 'P3', 191: '19L', 711: '71A',
                  712: '71B', 713: '71C', 714: '71D', 716: 'P16', 717: 'P17', 767: 'P67', 768: 'P68', 769: 'P69',
                  43: '43', 776: 'P76', 281: '28X', 801: 'O1', 805: 'O5', 812: 'O12', 913: 'P13', 900: 'G2', 903: 'G3',
                  907: 'P7', 910: 'P10', 912: 'P12', 401: 'Y1', 931: 'G31', 946: 'Y46', 947: 'Y47', 949: 'Y49',
                  444: 'P1', 445: 'Y45', 978: 'P78', 511: '51L'}


@curry
def parse(line, spec):
    start = spec.start
    end = spec.start + spec.length
    return spec.extract(line[start:end])


class StpFile(object):
    def __init__(self, fp, field_spec=None):
        self.fp = fp
        self.field_spec = field_spec or fields
        self.row_cls = namedtuple('StpRow', self.fields)

    @property
    def fields(self):
        return [s.name for s in self.field_spec]

    def lines(self):
        lineno = 0
        for line in self.fp:
            lineno += 1
            if lineno <= 3:
                continue
            if len(line) <= 284:
                continue
            yield line

    def readlines(self):
        for line in self.lines():
            yield self.row_cls(*map(parse(line), self.field_spec))


def to_model(data):
    return dict(
        day_of_week=data.day_of_week,
        direction=data.direction,
        route=route_name_map.get(data.route),
        trip=data.trip,
        block=dc.format_block_id(data.block),
        stop=data.stop,
        vehicle_id=data.vehicle_id,
        arrival_time=dc.to_datetime(data.year, data.month, data.day,
                                    data.arrival_hour, data.arrival_minute, data.arrival_second),
        departure_time=dc.to_datetime(data.year, data.month, data.day,
                                      data.departure_hour, data.departure_minute, data.departure_second),
        boarding=data.on,
        alighting=data.off,
        load=data.load,
        scheduled_arrival=dc.to_datetime(data.year, data.month, data.day,
                                         *map(int, dc.split_concatenated_time(data.scheduled_arrival))),
        predicted_travel_time=data.schedule_traveltime,
        actual_travel_time=data.actual_traveltime
    )


def etl_directory(path, session):
    for filename in filter(lambda s: s.endswith('.stp'), listdir(path)):
        logging.info("Reading APC-AVL from %s.", filename)
        with open(os.path.join(path, filename)) as fp:
            archive = StpFile(fp)
            logging.info("Saving created objects...")
            for rows in partition_all(100000, map(to_model, archive.readlines())):
                session.execute(ApcAvlRecord.__table__
                                            .insert()
                                            .values(rows))
                logging.info("Committing.")
                session.commit()
