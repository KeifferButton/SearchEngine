import subprocess
import time

spiders = [
    {"name": "quotes", "start_url": "https://quotes.toscrape.com/"},
    {"name": "books", "start_url": "https://books.toscrape.com/"},
    {"name": "toscrape", "start_url": "http://toscrape.com/"}
]

custom_settings = ["-s", "DEPTH_LIMIT=2", "-s", "LOG_LEVEL=INFO"]

processes = []

for spider in spiders:
    cmd = [
        "scrapy", "crawl", "generic",
        "-a", f"start_url={spider['start_url']}",
        "-a", f"spider_name={spider['name']}"
    ] + custom_settings
    
    print(f"Launching spider: {spider['name']}")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes.append((spider['name'], p))
    time.sleep(0.5)
    
try:
    # Wait and collect output
    for name, proc in processes:
        stdout, stderr = proc.communicate()
        print(f"\n===== {name} STDOUT =====\n")
        print(stdout.decode())
        print(f"\n===== {name} STDERR =====\n")
        print(stderr.decode())
except KeyboardInterrupt:
    print("\n Interrupted! Killing all spiders...")
    for name, proc in processes:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("All spiders terminated.")