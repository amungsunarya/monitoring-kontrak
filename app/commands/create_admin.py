import click
from flask.cli import with_appcontext
from app.database import execute
from app.extensions import bcrypt


@click.command('create-admin')
@click.option('--username', prompt=True, help='Username admin')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True, help='Password admin')
@click.option('--nama', prompt=True, help='Nama lengkap admin')
@with_appcontext
def create_admin_command(username, password, nama):
    """Buat user admin baru."""
    # Cek apakah username sudah ada
    existing = execute("SELECT id FROM users WHERE username=?", (username,))
    if existing:
        click.echo(f'Username "{username}" sudah dipakai. Coba username lain.')
        return

    hash_pw = bcrypt.generate_password_hash(password).decode()

    try:
        execute("""
            INSERT INTO users (username, password, nama, role)
            VALUES (?, ?, ?, 'admin')
        """, (username, hash_pw, nama), fetch=False)
        click.echo(f'Admin "{username}" berhasil dibuat!')
    except Exception as e:
        click.echo(f'Gagal: {e}')