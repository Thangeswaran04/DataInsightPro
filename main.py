import sqlite3
import datetime
import json
from typing import List, Dict, Union
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

class MemoryAssistant:
    def __init__(self, db_name: str = "memory.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            content TEXT,
            tags TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def store_memory(self, topic: str, content: str, tags: List[str] = None):
        cursor = self.conn.cursor()
        tags_str = json.dumps(tags) if tags else "[]"
        cursor.execute(
            "INSERT INTO memories (topic, content, tags) VALUES (?, ?, ?)",
            (topic, content, tags_str)
        )
        self.conn.commit()
        return "Memory stored successfully!"

    def search_memories(self, query: str) -> List[Dict[str, Union[str, datetime.datetime]]]:
        cursor = self.conn.cursor()
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT * FROM memories 
            WHERE topic LIKE ? OR content LIKE ? OR tags LIKE ?
            ORDER BY timestamp DESC
        """, (search_term, search_term, search_term))

        return self._format_results(cursor.fetchall())

    def get_all_memories(self) -> List[Dict[str, Union[str, datetime.datetime]]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM memories ORDER BY timestamp DESC")
        return self._format_results(cursor.fetchall())

    def _format_results(self, rows):
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'topic': row[1],
                'content': row[2],
                'tags': json.loads(row[3]),
                'timestamp': row[4]
            })
        return results

# Create global instance
assistant = MemoryAssistant()

@app.route('/')
def index():
    memories = assistant.get_all_memories()
    return render_template('index.html', memories=memories)

@app.route('/add_memory', methods=['POST'])
def add_memory():
    topic = request.form.get('topic')
    content = request.form.get('content')
    tags = request.form.get('tags', '').split(',')
    tags = [tag.strip() for tag in tags if tag.strip()]

    assistant.store_memory(topic, content, tags)
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        memories = assistant.search_memories(query)
    else:
        memories = []
    return render_template('search.html', memories=memories, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
