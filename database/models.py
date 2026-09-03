"""
SQLite schema. Only metadata lives here — actual product files always stay
in the Telegram storage channel; we only store channel_id + message_id.
"""
import os
import aiosqlite

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id         INTEGER PRIMARY KEY,
    username        TEXT,
    coin_balance    INTEGER NOT NULL DEFAULT 0,
    total_purchases INTEGER NOT NULL DEFAULT 0,
    referral_code   TEXT UNIQUE,
    referred_by     INTEGER,
    language        TEXT NOT NULL DEFAULT 'bn',
    is_banned       INTEGER NOT NULL DEFAULT 0,
    joined_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    icon        TEXT NOT NULL DEFAULT '📦',
    sort_order  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id   INTEGER,
    name          TEXT NOT NULL,
    description   TEXT NOT NULL DEFAULT '',
    price_coin    INTEGER NOT NULL DEFAULT 0,
    price_stars   INTEGER NOT NULL DEFAULT 0,
    storage_msg_id INTEGER NOT NULL,     -- message_id inside STORAGE_CHANNEL_ID
    preview_msg_id INTEGER,              -- optional preview/thumbnail message_id
    is_active     INTEGER NOT NULL DEFAULT 1,
    sales_count   INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    product_id     INTEGER NOT NULL,
    payment_method TEXT NOT NULL,        -- 'coin' | 'stars'
    amount_paid    INTEGER NOT NULL,
    coupon_code    TEXT,
    status         TEXT NOT NULL DEFAULT 'completed',   -- completed | refunded | failed
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS coin_transactions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    amount     INTEGER NOT NULL,          -- positive = credit, negative = debit
    reason     TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS referrals (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id   INTEGER NOT NULL,
    referred_id   INTEGER NOT NULL UNIQUE,
    reward_given  INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS coupons (
    code           TEXT PRIMARY KEY,
    discount_type  TEXT NOT NULL,          -- 'percent' | 'fixed_coin'
    discount_value INTEGER NOT NULL,
    usage_limit    INTEGER NOT NULL DEFAULT 0,   -- 0 = unlimited
    used_count     INTEGER NOT NULL DEFAULT 0,
    expires_at     TEXT,
    is_active      INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS coupon_usage (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL,
    user_id     INTEGER NOT NULL,
    used_at     TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(code, user_id)
);

CREATE TABLE IF NOT EXISTS admin_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id   INTEGER NOT NULL,
    action     TEXT NOT NULL,
    details    TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


async def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


def get_conn() -> aiosqlite.Connection:
    """Each caller should `async with get_conn() as db:`."""
    return aiosqlite.connect(DB_PATH)
