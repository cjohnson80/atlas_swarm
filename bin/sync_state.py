import json, os, re
def sync():
    hb_path = 'core/HEARTBEAT.md'
    pa_path = 'core/PENDING_ACTIONS.json'
    if not os.path.exists(hb_path): return
    with open(hb_path, 'r') as f: content = f.read()
    tasks = re.findall(r'- \[([x >])\] \*\*(.*?):\*\* (.*)', content)
    actions = [{"task": t[1], "status": t[0], "desc": t[2]} for t in tasks]
    with open(pa_path, 'w') as f: json.dump(actions, f, indent=2)
    print(f"[ATLAS_SYNC] Synchronized {len(actions)} tasks to PENDING_ACTIONS.json")
if __name__ == '__main__': sync()
