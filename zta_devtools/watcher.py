from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from zta_devtools.project_scan import scan_project

class PythonChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"\n📂 Changes detected in {event.src_path}")
            scan_project()

def start_watch(path="."):
    print(f"👀 Watching for changes in {path} (Ctrl+C to stop)...")
    event_handler = PythonChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
