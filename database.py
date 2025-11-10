import aiosqlite
from typing import Optional, Tuple, List, Any

async def connect_db():
    return await aiosqlite.connect("dating.db")

async def init_db():
    db = await connect_db()
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            city TEXT,
            gender TEXT,
            bio TEXT,
            photo_id TEXT,
            search_gender TEXT,
            search_age_min INTEGER,
            search_age_max INTEGER,
            username TEXT,
            view_count INTEGER DEFAULT 0
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            from_id INTEGER,
            to_id INTEGER,
            UNIQUE(from_id, to_id)
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS views (
            viewer_id INTEGER,
            viewed_id INTEGER,
            UNIQUE(viewer_id, viewed_id)
        )
    """)
    await db.commit()
    await db.close()

async def get_user_profile(user_id: int) -> Optional[Tuple]:
    db = await connect_db()
    async with db.execute(
        "SELECT name, age, city, gender, bio, photo_id FROM users WHERE user_id = ?",
        (user_id,)
    ) as cur:
        row = await cur.fetchone()
    await db.close()
    return row

async def update_user_view_count(user_id: int) -> int:
    db = await connect_db()
    await db.execute(
        "UPDATE users SET view_count = view_count + 1 WHERE user_id = ?",
        (user_id,)
    )
    async with db.execute(
        "SELECT view_count FROM users WHERE user_id = ?",
        (user_id,)
    ) as cur:
        view_count = (await cur.fetchone())[0]
    await db.commit()
    await db.close()
    return view_count

async def reset_user_view_count(user_id: int):
    db = await connect_db()
    await db.execute(
        "UPDATE users SET view_count = 0 WHERE user_id = ?",
        (user_id,)
    )
    await db.commit()
    await db.close()

async def get_user_view_count(user_id: int) -> int:
    db = await connect_db()
    async with db.execute(
        "SELECT view_count FROM users WHERE user_id = ?",
        (user_id,)
    ) as cur:
        result = await cur.fetchone()
    await db.close()
    return result[0] if result else 0

async def save_user_profile(user_id: int, data: dict, username: str):
    db = await connect_db()
    await db.execute(
        """INSERT OR REPLACE INTO users 
        (user_id, name, age, city, gender, bio, photo_id, username) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, data['name'], data['age'], data['city'], 
         data['gender'], data['bio'], data.get('photo_id'), username)
    )
    await db.commit()
    await db.close()

async def update_search_criteria(user_id: int, search_gender: str, age_min: int, age_max: int):
    db = await connect_db()
    await db.execute(
        "UPDATE users SET search_gender = ?, search_age_min = ?, search_age_max = ? WHERE user_id = ?",
        (search_gender, age_min, age_max, user_id)
    )
    await db.commit()
    await db.close()