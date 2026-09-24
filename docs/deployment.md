# Deployment Guide

## 1. Setup Server DB (10.88.20.7)

SSH ke server DB, lalu buat user & database:

```sql
CREATE USER 'kontrak_user'@'%' IDENTIFIED BY 'PasswordKuat123!';
GRANT ALL PRIVILEGES ON monitoring_kontrak.* TO 'kontrak_user'@'%';
FLUSH PRIVILEGES;

CREATE DATABASE monitoring_kontrak
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;