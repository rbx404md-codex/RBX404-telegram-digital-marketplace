"""
All database access goes through these helpers so handlers never write raw
SQL. Keeping it in one place also makes the backup/restore story simple —
the whole app's state is this one sqlite file.
"""
import secrets
import string
from datetime import datetime, timezone

from database.models import get_conn


def _gen_ref_code() -> str:
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))


# ---------------------------------------------------------------- users ----
async def get_or_create_user(user_id: int, username: str | None, referred_by_code: str | None = None) -> dict:
    async with get_conn() as db:
        db.row_factory = None
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))

        ref_code = _gen_ref_code()
        referred_by = None
        if referred_by_code:
            cur2 = await db.execute("SELECT user_id FROM users WHERE referral_code = ?", (referred_by_code,))
            r = await cur2.fetchone()
            if r and r[0] != user_id:
                referred_by = r[0]

        await db.execute(
            "INSERT INTO users (user_id, username, referral_code, referred_by) VALUES (?,?,?,?)",
            (user_id, username, ref_code, referred_by),
        )
        if referred_by:
            await db.execute(
                "INSERT OR IGNORE INTO referrals (referrer_id, referred_id) VALUES (?,?)",
                (referred_by, user_id),
            )
        await db.commit()

        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


async def get_user(user_id: int) -> dict | None:
    async with get_conn() as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


async def set_ban(user_id: int, banned: bool) -> None:
    async with get_conn() as db:
        await db.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (int(banned), user_id))
        await db.commit()


# ---------------------------------------------------------------- coins ----
async def adjust_coins(user_id: int, amount: int, reason: str) -> int:
    """amount can be negative. Returns new balance. Raises ValueError if insufficient."""
    async with get_conn() as db:
        cur = await db.execute("SELECT coin_balance FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        balance = row[0] if row else 0
        new_balance = balance + amount
        if new_balance < 0:
            raise ValueError("Insufficient coin balance")

        await db.execute("UPDATE users SET coin_balance = ? WHERE user_id = ?", (new_balance, user_id))
        await db.execute(
            "INSERT INTO coin_transactions (user_id, amount, reason) VALUES (?,?,?)",
            (user_id, amount, reason),
        )
        await db.commit()
        return new_balance


async def coin_history(user_id: int, limit: int = 15) -> list[dict]:
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT amount, reason, created_at FROM coin_transactions "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


# ----------------------------------------------------------- categories ----
async def list_categories() -> list[dict]:
    async with get_conn() as db:
        cur = await db.execute("SELECT * FROM categories ORDER BY sort_order, name")
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


async def add_category(name: str, icon: str = "📦") -> int:
    async with get_conn() as db:
        cur = await db.execute("INSERT INTO categories (name, icon) VALUES (?,?)", (name, icon))
        await db.commit()
        return cur.lastrowid


# -------------------------------------------------------------- products ---
async def list_products(category_id: int | None = None, active_only: bool = True) -> list[dict]:
    q = "SELECT * FROM products WHERE 1=1"
    params: list = []
    if category_id is not None:
        q += " AND category_id = ?"
        params.append(category_id)
    if active_only:
        q += " AND is_active = 1"
    q += " ORDER BY sales_count DESC, product_id DESC"
    async with get_conn() as db:
        cur = await db.execute(q, params)
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


async def get_product(product_id: int) -> dict | None:
    async with get_conn() as db:
        cur = await db.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = await cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


async def add_product(category_id: int, name: str, description: str, price_coin: int,
                       price_stars: int, storage_msg_id: int, preview_msg_id: int | None = None) -> int:
    async with get_conn() as db:
        cur = await db.execute(
            "INSERT INTO products (category_id, name, description, price_coin, price_stars, "
            "storage_msg_id, preview_msg_id) VALUES (?,?,?,?,?,?,?)",
            (category_id, name, description, price_coin, price_stars, storage_msg_id, preview_msg_id),
        )
        await db.commit()
        return cur.lastrowid


async def set_product_active(product_id: int, active: bool) -> None:
    async with get_conn() as db:
        await db.execute("UPDATE products SET is_active = ? WHERE product_id = ?", (int(active), product_id))
        await db.commit()


async def bump_sales(product_id: int) -> None:
    async with get_conn() as db:
        await db.execute("UPDATE products SET sales_count = sales_count + 1 WHERE product_id = ?", (product_id,))
        await db.commit()


# ----------------------------------------------------------------- orders --
async def create_order(user_id: int, product_id: int, payment_method: str,
                        amount_paid: int, coupon_code: str | None = None) -> int:
    async with get_conn() as db:
        cur = await db.execute(
            "INSERT INTO orders (user_id, product_id, payment_method, amount_paid, coupon_code) "
            "VALUES (?,?,?,?,?)",
            (user_id, product_id, payment_method, amount_paid, coupon_code),
        )
        await db.execute(
            "UPDATE users SET total_purchases = total_purchases + 1 WHERE user_id = ?", (user_id,)
        )
        await db.commit()
        return cur.lastrowid


async def has_purchased(user_id: int, product_id: int) -> bool:
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT 1 FROM orders WHERE user_id=? AND product_id=? AND status='completed'",
            (user_id, product_id),
        )
        return (await cur.fetchone()) is not None


async def user_orders(user_id: int, limit: int = 20) -> list[dict]:
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT o.*, p.name as product_name FROM orders o "
            "JOIN products p ON p.product_id = o.product_id "
            "WHERE o.user_id = ? ORDER BY o.order_id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


# --------------------------------------------------------------- coupons ---
async def get_coupon(code: str) -> dict | None:
    async with get_conn() as db:
        cur = await db.execute("SELECT * FROM coupons WHERE code = ?", (code.upper(),))
        row = await cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


async def create_coupon(code: str, discount_type: str, discount_value: int,
                         usage_limit: int = 0, expires_at: str | None = None) -> None:
    async with get_conn() as db:
        await db.execute(
            "INSERT INTO coupons (code, discount_type, discount_value, usage_limit, expires_at) "
            "VALUES (?,?,?,?,?)",
            (code.upper(), discount_type, discount_value, usage_limit, expires_at),
        )
        await db.commit()


async def redeem_coupon(code: str, user_id: int) -> None:
    async with get_conn() as db:
        await db.execute(
            "INSERT INTO coupon_usage (code, user_id) VALUES (?,?)", (code.upper(), user_id)
        )
        await db.execute(
            "UPDATE coupons SET used_count = used_count + 1 WHERE code = ?", (code.upper(),)
        )
        await db.commit()


async def coupon_already_used(code: str, user_id: int) -> bool:
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT 1 FROM coupon_usage WHERE code=? AND user_id=?", (code.upper(), user_id)
        )
        return (await cur.fetchone()) is not None


def coupon_is_valid(coupon: dict) -> tuple[bool, str]:
    if not coupon or not coupon["is_active"]:
        return False, "কুপনটি খুঁজে পাওয়া যায়নি বা নিষ্ক্রিয়।"
    if coupon["usage_limit"] and coupon["used_count"] >= coupon["usage_limit"]:
        return False, "কুপনের ব্যবহার সীমা শেষ হয়ে গেছে।"
    if coupon["expires_at"]:
        try:
            exp = datetime.fromisoformat(coupon["expires_at"])
            if datetime.now(timezone.utc).replace(tzinfo=None) > exp:
                return False, "কুপনের মেয়াদ শেষ হয়ে গেছে।"
        except ValueError:
            pass
    return True, ""


# -------------------------------------------------------------- referral ---
async def mark_referral_rewarded(referred_id: int) -> int | None:
    """Called on a referred user's FIRST purchase. Returns referrer_id if rewarded now."""
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT referrer_id, reward_given FROM referrals WHERE referred_id = ?", (referred_id,)
        )
        row = await cur.fetchone()
        if not row or row[1]:
            return None
        referrer_id = row[0]
        await db.execute(
            "UPDATE referrals SET reward_given = 1 WHERE referred_id = ?", (referred_id,)
        )
        await db.commit()
        return referrer_id


async def referral_stats(user_id: int) -> dict:
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT COUNT(*), SUM(reward_given) FROM referrals WHERE referrer_id = ?", (user_id,)
        )
        total, rewarded = await cur.fetchone()
        return {"total": total or 0, "rewarded": rewarded or 0}


async def referral_leaderboard(limit: int = 10) -> list[dict]:
    async with get_conn() as db:
        cur = await db.execute(
            "SELECT referrer_id, COUNT(*) as cnt FROM referrals "
            "GROUP BY referrer_id ORDER BY cnt DESC LIMIT ?",
            (limit,),
        )
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]


# ------------------------------------------------------------- analytics ---
async def sales_summary() -> dict:
    async with get_conn() as db:
        cur = await db.execute("SELECT COUNT(*), COALESCE(SUM(amount_paid),0) FROM orders WHERE payment_method='stars'")
        stars_orders, stars_revenue = await cur.fetchone()
        cur = await db.execute("SELECT COUNT(*), COALESCE(SUM(amount_paid),0) FROM orders WHERE payment_method='coin'")
        coin_orders, coin_revenue = await cur.fetchone()
        cur = await db.execute("SELECT COUNT(*) FROM users")
        (total_users,) = await cur.fetchone()
        cur = await db.execute("SELECT COUNT(*) FROM products WHERE is_active=1")
        (active_products,) = await cur.fetchone()
        return {
            "stars_orders": stars_orders, "stars_revenue": stars_revenue,
            "coin_orders": coin_orders, "coin_revenue": coin_revenue,
            "total_users": total_users, "active_products": active_products,
        }
