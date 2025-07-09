import sys
from query_engine import search

if __name__ == "__main__":
    query = sys.argv[1]
    use_raw_query = bool(int(sys.argv[2])) if len(sys.argv) > 2 else False
    results = search(query, use_raw_query)
    for r in results:
        print(r)
