from flask import Flask, request, jsonify, render_template
from mem0 import MemoryClient
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = Flask(__name__)
mem0_client = MemoryClient()
DEFAULT_USER_ID = "chrome-extension-user"

@app.route('/')
def index():
    return render_template('memories_api.html')

@app.route('/memories', methods=['GET'])
def list_memories():
    category = request.args.get('category')
    memory_regex = request.args.get('memory_regex')
    memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=100)
    results = memories["results"]
    if category:
        results = [m for m in results if category in (m.get("categories") or [])]
    if memory_regex:
        try:
            pattern = re.compile(memory_regex, re.IGNORECASE)
            results = [m for m in results if m.get("memory") and pattern.search(m.get("memory"))]
        except re.error:
            return jsonify({"error": "Invalid regex pattern"}), 400
    # Flatten for table
    table = [
        {
            "id": m["id"],
            "memory": m.get("memory"),
            "categories": m.get("categories"),
            "created_at": m.get("created_at"),
        }
        for m in results
    ]
    return jsonify(table)

@app.route('/memories', methods=['DELETE'])
def delete_memories():
    ids = request.json.get('ids', [])
    errors = []
    for memory_id in ids:
        try:
            mem0_client.delete(memory_id=memory_id)
        except Exception as e:
            errors.append({"id": memory_id, "error": str(e)})
    return jsonify({"deleted": ids, "errors": errors})

if __name__ == '__main__':
    app.run(port=5000, debug=True) 