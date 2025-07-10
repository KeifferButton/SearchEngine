from flask import Flask, request, jsonify, render_template
from query_engine import search

app = Flask(__name__)

@app.route("/search", methods=["GET"])
def handle_search():
    query = request.args.get("q")
    use_raw = request.args.get("raw", "false").lower() == "true"
    
    if not query:
        return jsonify({"error": "Missing query"}), 400
    
    results, original_query, corrected_query = search(query, use_raw_query=use_raw)
    
    return jsonify({
        "original_query": original_query,
        "corrected_query": corrected_query,
        "used_raw_query": use_raw,
        "results": results
    })
    
@app.route("/")
def index():
    return render_template("index.html")
    
if __name__ == "__main__":
    app.run(debug=True)