import os
import sys
import json
import urllib.request
import urllib.error
import time

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS_PATH = os.path.join(SCRIPT_DIR, "urls.json")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

def main():
    if os.path.exists(URLS_PATH):
        path = URLS_PATH
    else:
        path = CONFIG_PATH
    with open(path, encoding="utf-8") as f:
        sw_list = json.load(f)
    if path == CONFIG_PATH:
        sw_list = sw_list.get("software", {})

    results = {"ok": 0, "fail": 0, "skipped": 0}
    for name, sw in sw_list.items():
        url = sw.get("url", "")
        if not url or sw.get("type") == "winget":
            results["skipped"] += 1
            continue
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            resp = urllib.request.urlopen(req, timeout=15)
            if resp.status < 400:
                print(f"  OK  {name:25s} {resp.status} {url[:70]}")
                results["ok"] += 1
            else:
                print(f" WARN {name:25s} HTTP {resp.status} {url[:70]}")
                results["fail"] += 1
        except urllib.error.HTTPError as e:
            print(f" FAIL {name:25s} HTTP {e.code} {url[:70]}")
            results["fail"] += 1
        except Exception as e:
            print(f" FAIL {name:25s} {str(e)[:50]} {url[:70]}")
            results["fail"] += 1

    print(f"\nDone: {results['ok']} OK, {results['fail']} FAIL, {results['skipped']} skipped (winget)")

if __name__ == "__main__":
    main()
