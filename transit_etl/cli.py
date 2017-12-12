import click
from transit_etl import models, gtfs, stp
from transit_etl.db import Database

@click.group()
def cli():
    pass


@cli.command()
@click.option('--database-url', required=True, help="Database url e.g.: mysql://user:pw@localhost/transit")
def createdb(database_url):
    """Create the GTFS/APC-AVL schema."""
    db = Database(database_url)
    models.Base.metadata.create_all(db.engine)


@cli.command()
@click.option('--database-url', required=True, help="Database url e.g.: mysql://user:pw@localhost/transit")
@click.option('--gtfs-path', type=click.Path(exists=True), help="Path to a folder of GTFS zip files")
@click.option('--stp-path', type=click.Path(exists=True), help="Path to a folder of APC-AVL .stp files")
def etl(database_url, gtfs_path=None, stp_path=None):
    """Load GTFS and APC-AVL data into a database."""
    db = Database(database_url)
    with db.session() as session:
        if gtfs_path:
            gtfs.etl_directory(gtfs_path, session)
        if stp_path:
            stp.etl_directory(stp_path, session)