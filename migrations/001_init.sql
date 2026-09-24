-- ============================================================
-- Monitoring Kontrak - SQLite Schema
-- ============================================================

-- ==================== USERS ====================
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  nama TEXT NOT NULL,
  role TEXT DEFAULT 'user' CHECK(role IN ('admin','user','viewer')),
  telegram_chat_id TEXT,
  aktif INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ==================== KONTRAK ====================
CREATE TABLE IF NOT EXISTS kontrak (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  no_kontrak TEXT UNIQUE NOT NULL,
  uraian_pekerjaan TEXT,
  jenis TEXT,
  link_dokumen TEXT,
  vendor TEXT,
  status_pekerjaan TEXT DEFAULT 'Berjalan',
  awal_kontrak DATE NOT NULL,
  akhir_kontrak DATE NOT NULL,
  progres_bayar INTEGER DEFAULT 0,
  progres_fisik INTEGER DEFAULT 0,
  termin TEXT,
  update_lkp DATE,
  catatan TEXT,
  akhir_jampel DATE,
  akhir_jamhar DATE,
  masa_pemeliharaan TEXT,
  akhir_amandemen DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kontrak_no ON kontrak(no_kontrak);
CREATE INDEX IF NOT EXISTS idx_kontrak_vendor ON kontrak(vendor);
CREATE INDEX IF NOT EXISTS idx_kontrak_awal ON kontrak(awal_kontrak);
CREATE INDEX IF NOT EXISTS idx_kontrak_akhir ON kontrak(akhir_kontrak);

-- ==================== LOG AKTIVITAS ====================
CREATE TABLE IF NOT EXISTS log_aktivitas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  aksi TEXT,
  keterangan TEXT,
  ip TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_log_user ON log_aktivitas(user_id);
CREATE INDEX IF NOT EXISTS idx_log_created ON log_aktivitas(created_at);

-- ==================== TRIGGERS: auto update updated_at ====================
CREATE TRIGGER IF NOT EXISTS trg_users_updated
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
  UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_kontrak_updated
AFTER UPDATE ON kontrak
FOR EACH ROW
BEGIN
  UPDATE kontrak SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;