# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from config import DB_PATH

class SearchEnginePipeline:
    def open_spider(self, spider):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Pages table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                text TEXT
            )
        ''')
        
        # Images table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                page_id INTEGER,
                FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE CASCADE
            )
        ''')
        
        self.connection.commit()
        
    def close_spider(self, spider):
        self.connection.close()
    
    def process_item(self, item, spider):
        # Insert page, ignoring duplicates
        page_id = None
        try:
            self.cursor.execute('''
                INSERT INTO pages (url, title, text)
                VALUES (?, ?, ?)
            ''', (
                item.get('url'),
                item.get('title'),
                item.get('text'),
            ))
            page_id = self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Page already exists, fetch its ID
            self.cursor.execute('SELECT id FROM pages WHERE url = ?', (item.get('url'),))
            result = self.cursor.fetchone()
            page_id = result[0] if result else None
        
        # Insert images linked to this page
        if page_id:
            for image_url in item.get('images', []):
                try:
                    self.cursor.execute('''
                        INSERT INTO images (url, page_id)
                        VALUES (?, ?)
                    ''', (image_url, page_id))
                except sqlite3.IntegrityError:
                    # Image already exists — ignore
                    pass
        
        self.connection.commit()
        return item
