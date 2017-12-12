"""Read and import gtfs files"""
import logging
import csv
import zipfile

from os import listdir
import os.path
from itertools import ifilter

from transit_etl import models


from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert


model_map = (
    ('agency', models.Agency),
    ('calendar', models.Calendar),
    ('calendar_dates', models.CalendarDate),
    ('routes', models.Route),
    ('shapes', models.Shape),
    ('stops', models.Stop),
    ('stop_times', models.StopTime),
    ('transfers', models.Transfer),
    ('trips', models.Trip),
)


class GtfsZip(object):
    def __init__(self, filename):
        self.filename = filename
        self._zipfile = zipfile.ZipFile(filename)

    def rows(self, item):
        name = "{}.txt".format(item)
        return csv.DictReader(self._zipfile.open(name))


@compiles(Insert, 'mysql')
def replace(insert, compiler, **kw):
    s = compiler.visit_insert(insert, **kw)
    if insert.kwargs.get('mysql_replace'):
        s = s.replace('INSERT', 'REPLACE')
    return s
Insert.argument_for('mysql', 'replace', False)


def etl_directory(path, session):
    for filename in filter(lambda s: s.endswith('.zip'), listdir(path)):
        logging.info("Reading GTFS from %s.", filename)
        archive = GtfsZip(os.path.join(path, filename))
        logging.info("Saving created objects...")
        for name, cls in model_map:
            for row in ifilter(None, archive.rows(name)):
                stmt = (cls.__table__
                           .insert(mysql_replace=True))
                session.execute(stmt, row)