import click
from flask.cli import with_appcontext


@click.command('sync-sheets')
@with_appcontext
def sync_sheets_command():
    """Sync manual semua kontrak ke Google Sheets."""
    from app.services.sheets_service import SheetsService
    try:
        result = SheetsService.sync_all()
        if result:
            click.echo('Sync ke Google Sheets berhasil!')
        else:
            click.echo('Sync gagal, cek log untuk detail.')
    except Exception as e:
        click.echo(f'Error: {e}')