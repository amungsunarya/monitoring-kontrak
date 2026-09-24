#!/bin/bash
# ============================================================
# Setup database awal di server 10.88.20.7
# Jalankan dari komputer yang punya akses ke DB server
# ============================================================

DB_HOST="10.88.20.7"
DB_USER="root"
DB_PASS="password_root_db_anda"

echo "Setup database di $DB_HOST..."

mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" < migrations/001_init.sql

if [ $? -eq 0 ]; then
    echo "Database berhasil dibuat!"
    echo ""
    echo "Cek dengan:"
    echo "  mysql -h $DB_HOST -u $DB_USER -p -e 'SHOW TABLES' monitoring_kontrak"
else
    echo "Gagal setup database. Cek koneksi & kredensial."
    exit 1
fi