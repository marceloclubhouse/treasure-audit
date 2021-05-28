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

import re
from auditor import WebPage
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

    def find_all_pages(self, current_page: WebPage, traversed_pages=dict()) -> {str: WebPage}:
        """
        Crawl a WebPage recursively and return a dictionary
        of all the internal pages that can be traversed from
        that URL.
        """
        # Add current page WebPage object to the traversed
        # pages dictionary, with URL string as its key
        traversed_pages[current_page.get_url()] = current_page

        for p in current_page.get_internal_links():
            if p not in traversed_pages and re.match(WebPage.URL_REGEX, p):

                # Try to create a WebPage object from each URL found,
                # but if there's something wrong with the anchor,
                # such as it lacking a href value or linking to a
                # page that generates an error, just skip
                # that page and continue crawling.
                try:
                    self.signals.pages_crawled.emit(traversed_pages)
                    traversed_pages.update(self.find_all_pages(WebPage(p), traversed_pages))
                except Exception as e:
                    print(f"Error crawling {p}: {e}")

        return traversed_pages

    @pyqtSlot()
    def run(self) -> None:
        """
        Crawl a WebPage recursively and emit a dictionary of
        all WebPages found in the form {url_str: WebPage}
        """

        try:
            self.pages = self.find_all_pages(WebPage(self.url))
            self.signals.pages_crawled.emit(self.pages)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


if __name__ == '__main__':
    pass
