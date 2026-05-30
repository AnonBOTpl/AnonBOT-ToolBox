import os
import socket
import urllib.request
import urllib.error
import shutil
from PyQt6.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    status = pyqtSignal(str)

    def __init__(self, url, output_path, parent=None):
        super().__init__(parent)
        self.url = url
        self.output_path = output_path
        self._cancelled = False
        self._response = None
        self.chunk_size = 16384

    def run(self):
        try:
            self.status.emit("Downloading...")
            dirname = os.path.dirname(self.output_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            req = urllib.request.Request(
                self.url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            self._response = urllib.request.urlopen(req, timeout=30)
            try:
                self._response.fp.raw._sock.settimeout(1)
            except Exception:
                pass
            total = int(self._response.headers.get("Content-Length", 0))
            downloaded = 0
            with open(self.output_path, "wb") as f:
                while not self._cancelled:
                    try:
                        chunk = self._response.read(self.chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = int(downloaded * 100 / total)
                            self.progress.emit(pct)
                    except socket.timeout:
                        continue
                    except Exception:
                        break

            if self._cancelled:
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)
                self.finished.emit(False, "Cancelled")
            else:
                self.finished.emit(True, self.output_path)
        except urllib.error.HTTPError as e:
            self.finished.emit(False, f"HTTP {e.code} {e.reason}")
        except urllib.error.URLError as e:
            self.finished.emit(False, f"Connection error: {e.reason}")
        except Exception as e:
            self.finished.emit(False, str(e))
        finally:
            if self._response:
                try:
                    self._response.close()
                except Exception:
                    pass

    def cancel(self):
        self._cancelled = True
        if self._response:
            try:
                self._response.close()
            except Exception:
                pass


class DownloadManager:
    def __init__(self, parent=None):
        self._threads = []

    def _remove_thread(self, thread):
        try:
            self._threads.remove(thread)
        except ValueError:
            pass

    def download(self, url, output_path):
        thread = DownloadThread(url, output_path)
        self._threads.append(thread)
        thread.finished.connect(lambda t=thread: self._remove_thread(t))
        thread.start()
        return thread

    def cancel_all(self):
        for t in self._threads:
            t.cancel()
