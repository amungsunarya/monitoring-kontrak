import os
import click
from flask import current_app
from flask.cli import with_appcontext
from app.database import get_db


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Buat database SQLite & tabel dari migrations/001_init.sql."""
    sql_file = os.path.join('migrations', '001_init.sql')
    if not os.path.exists(sql_file):
        click.echo(f'File {sql_file} tidak ditemukan!')
        return

    with open(sql_file, 'r', encoding='utf-8') as f:
        schema = f.read()

    db = get_db()
    try:
        db.executescript(schema)
        db.commit()

        db_path = current_app.config['DB_PATH']
        click.echo(f'Database berhasil dibuat: {db_path}')

        cur = db.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall() if not r[0].startswith('sqlite_')]
        click.echo(f'Total {len(tables)} tabel:')
        for t in tables:
            click.echo(f'   - {t}')
    except Exception as e:
        click.echo(f'Gagal: {e}')