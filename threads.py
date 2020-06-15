"""
Treasure Audit - threads.py

Threads contains PyQt objects that work with auditor.py.
By integrating the auditing portion of the software in threads,
the GUI will create new threads to crawl websites instead of
running the scripts in the main thread, thus preventing
unresponsiveness.

Revisions:
- 2020/06/15 : First revision

Copyright (C) 2020 Marcelo Cubillos
This software is licensed under the GPL v3, see LICENSE.txt
for more information.
"""

from auditor import WebPage, find_all_pages
from PyQt5.Qt import QRunnable, pyqtSlot, pyqtSignal, QObject


class CrawlerSignals(QObject):
    """
    The CrawlerSignals class is used by the Crawler
    class to emit signals. These signals can then be
    connected to methods within the main application,
    when referenced from the Crawler class and called
    within the Interface class.
    """
    pages_crawled = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)


class CrawlerThread(QRunnable):
    """
    CrawlerThread class represents a separate thread
    within the main application that uses the auditor
    script to generate a dictionary of WebPage objects.

    The CrawlerThread class does not return any objects
    but emits a dictionary of WebPages organized by their
    URL's as strings once the auditing script is done
    executing.
    """

    def __init__(self, url: str):
        super(CrawlerThread, self).__init__()
        self.url = url
        self.signals = CrawlerSignals()
        self.pages = dict()

    @pyqtSlot()
    def run(self) -> None:
        """
        Crawl a WebPage recursively and emit a dictionary of
        all WebPages found in the form {url_str: WebPage}
        """
        try:
            self.pages = find_all_pages(WebPage(self.url))
            self.signals.pages_crawled.emit(self.pages)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


if __name__ == '__main__':
    pass
