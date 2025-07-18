from flask import Flask, request, jsonify, render_template
from query_engine import search

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search_route():
    query = request.args.get('q', '')
    raw = request.args.get('raw') == 'true'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX fetch from JS, return JSON
        results, original_query, corrected_query = search(query, use_raw_query=raw)
        return jsonify({
            "results": results,
            "original_query": original_query,
            "corrected_query": corrected_query,
            "used_raw_query": raw
        })
    else:
        # If it's a browser visit from home.html, render search page
        return render_template("search.html")
    
if __name__ == "__main__":
    app.run(debug=True)