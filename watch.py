import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from paramiko_sync import setup_connection, create_file, create_directory, moved_file_or_dir, deleted_file, remove_directory

# Watchdog Tryout
# class Watcher(FileSystemEventHandler):
#     def on_created(self, event):
#         print("File created: ", event.src_path)
#         return super().on_created(event)
#     def on_moved(self, event):
#         print("File moved: ", event.src_path)
#         return super().on_moved(event)
#     def on_deleted(self, event):
#         print("File deleted: ", event.src_path)
#         return super().on_deleted(event)
#     def on_modified(self, event):
#         print("File modified: ", event.src_path)
#         return super().on_modified(event)

def standardiser(event_path):
    return event_path.replace("\\","/")

class Watcher(FileSystemEventHandler):
    def __init__(self, syncer):
        self.last_modified = {}
        super().__init__()
        self.syncer = syncer
    def on_created(self, event):
        self.syncer.last_event_time = time.monotonic()
        if event.is_directory:
            final_path = standardiser(event.src_path)
            create_directory(final_path=final_path)
            print("Directory created: ", final_path)
        else:
            final_path = standardiser(event.src_path)
            create_file(final_path=final_path)
            print("File created: ", final_path)
        return super().on_created(event)
    def on_moved(self, event):
        self.syncer.last_event_time = time.monotonic()
        initial_name = standardiser(event.src_path)
        final_name = standardiser(event.dest_path)
        moved_file_or_dir(initial_name=initial_name, final_name=final_name)
        print("File moved: ", initial_name)
        print("File moved to: ", final_name)
        return super().on_moved(event)
    def on_deleted(self, event):
        self.syncer.last_event_time = time.monotonic()
        if event.is_directory:
            final_path = standardiser(event.src_path)
            final_path = final_path.lstrip("./")
            final_path = "/home/keoni/sync_folder/" + final_path
            print(final_path == "/home/keoni/sync_folder/hello")
            # client = setup_connection()
            # sftp = client.open_sftp()
            # remove_directory(sftp, final_path)
            # sftp.close()
            # client.close()
            print("Directory deleted: ", event.src_path)
        else:
            final_path = standardiser(event.src_path)
            deleted_file(final_path)
            print("File deleted: ", final_path)
        return
    def on_modified(self, event):
        self.syncer.last_event_time = time.monotonic()
        if event.is_directory:
            return
        else:
            print("File modified: ", event.src_path)
        return super().on_modified(event)
    # def on_any_event(self, event):
    #     self.syncer.last_event_time = time.monotonic()
    #     print(event.src_path)
    #     return super().on_any_event(event)

class Timer(threading.Thread):
    def __init__(self, syncer):
        super().__init__()
        self.syncer = syncer
    def run(self):
        while self.syncer.online:
            if self.syncer.last_event_time == None:
                time.sleep(1)
                continue
            if (time.monotonic() - self.syncer.last_event_time >= 10):
                print("schedule for sync")
                self.syncer.last_sync_time = time.monotonic()
                self.syncer.last_event_time = None
            time.sleep(0.5)

class Syncer():
    def __init__(self):
        self.last_event_time = None
        self.last_sync_time = time.monotonic()
        self.online = True

def main():
    syncer = Syncer()
    timer = Timer(syncer)
    timer.start()
    observer = Observer()
    handler = Watcher(syncer)
    observer.schedule(handler, ".", recursive=True)
    observer.start()
    
    while True:
        cmd = input("q to quit: ")
        if cmd == "q":
            syncer.online = False
            observer.stop()
            observer.join()
            timer.join()
            break

if __name__ == "__main__":
    main()