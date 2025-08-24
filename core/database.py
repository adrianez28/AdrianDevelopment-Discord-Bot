import sqlite3

# Class to manage database connections and operations
class Database:

    def __init__(self):

        self.db = sqlite3.connect("db/database.db", check_same_thread=False)
        self.cursor = self.db.cursor()   
        self.tables()

    def tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT,
                purchases INTEGER,
                spent_money REAL
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS active_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT,
                active TEXT
            )
            """
        )
        self.db.commit()

    #Add user to database
    def add_user(self, discord_id, purchases=0, spent_money=0):
        self.cursor.execute(
            """
            INSERT INTO users (discord_id, purchases, spent_money) VALUES (?, ?, ?)
            """,
            (discord_id, purchases, spent_money)
        )
        self.db.commit()

    #Add active conversation to database
    def add_active_conversation(self, discord_id, active="1"):
        self.cursor.execute(
            """
            INSERT INTO active_conversations (discord_id, active) VALUES (?, ?)
            """,
            (discord_id, active)
        )
        self.db.commit()

    #Remove active conversation from database
    def remove_active_conversation(self, discord_id):
        self.cursor.execute(
            """
            DELETE FROM active_conversations WHERE discord_id = ?
            """,
            (discord_id,)
        )
        self.db.commit()

    #Add purchase to database
    def add_purchase(self, discord_id, amount):
        self.cursor.execute(
            """
            UPDATE users SET purchases = purchases + 1, spent_money = spent_money + ? WHERE discord_id = ?
            """,
            (amount, discord_id)
        )
        self.db.commit()

    #Get user from database
    def get_user(self, discord_id):
        user = self.cursor.execute(
            """
            SELECT * FROM users WHERE discord_id = ?
            """,
            (discord_id,)
        )

        if user.fetchone():
            return user.fetchone()
        return None

    #Get active conversations for user from database
    def get_active_conversations_user(self, discord_id):
        user = self.cursor.execute(
            """
            SELECT * FROM active_conversations WHERE discord_id = ?
            """,
            (discord_id,)
        )

        if user.fetchone():
            return True
        return False
