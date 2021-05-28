"""
Treasure Audit - interfaces.py

Interfaces contains the script for the main GUI. It inherits
all of the visual elements from main_window.py and connects
every element of the UI to different methods contained within
the inheritance.

Revisions:
- 2021/05/28 : Updated threads to refresh UI for every page
               crawled
- 2020/07/20 : Replaced criteria attributes from inclusion/
               exclusion to inclusion, ignored, and exclusion
- 2020/07/07 : Removed HTML criteria functionality; replaced
               it with inclusion criteria/exclusion criteria
- 2020/06/15 : First revision

Copyright (C) 2020 Marcelo Cubillos
This software is licensed under the GPL v3, see LICENSE.txt
for more information.
"""

from PyQt5.QtCore import Qt
from PyQt5.Qt import QThreadPool
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog
from PyQt5.QtGui import QTextBlockFormat, QTextCursor, QIcon, QPixmap
from auditor import WebPage, has_text, does_not_have_text
from main_window import Ui_MainWindow
from about_window import Ui_Dialog_about
from threads import CrawlerThread
from webbrowser import open_new
import re
from sys import exit
from datetime import date
import os
import sys


class Window:
    """
    Abstract base class for defining GUI windows
    """
    @staticmethod
    def resource_path(relative_path):
        """
        Get absolute path to resource. Used from:
        https://stackoverflow.com/questions/52654805/
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    @staticmethod
    def _quit():
        """
        Close the application.
        """
        exit()


class AboutWindow(Window, QDialog, Ui_Dialog_about):
    """
    A callable GUI interface for the about window
    """

    def __init__(self):
        super(AboutWindow, self).__init__()
        self.setupUi(self)
        self.label_logo.setPixmap(QPixmap(self.resource_path('resources/icon_logo.png')))


class AuditInterface(Window, QMainWindow, Ui_MainWindow):
    """
    The AuditInterface class represents a callable
    GUI interface.

    The methods contained within this class are
    connected to the visual widgets of
    main_window.Ui_MainWindow and make the interface
    functional.
    """

    HELP_URL = 'https://github.com/marceloclubhouse/treasure-audit'
    CONTAINER_REGEX = re.compile("^<?(?P<container>(?:[A-z]|\-|\_|[0-9]|\.)+)>?$")

    def __init__(self):

        super(AuditInterface, self).__init__()
        self.setupUi(self)
        self._currently_crawling = False
        self._highlight_pages = False

        self.about_window = AboutWindow()
        self.thread_pool = QThreadPool()

        # Import/set icons
        self.setWindowIcon(QIcon(self.resource_path('resources/icon_logo.ico')))
        self.actionImport.setIcon(QIcon(self.resource_path('feather/upload.svg')))
        self.actionExport.setIcon(QIcon(self.resource_path('feather/download.svg')))
        self.actionQuit.setIcon(QIcon(self.resource_path('feather/x-octagon.svg')))
        self.actionCrawl.setIcon(QIcon(self.resource_path('feather/layers.svg')))
        self.actionOpen_Page_in_Web_Browser.setIcon(QIcon(self.resource_path('feather/external-link.svg')))
        self.actionClear_Criteria.setIcon(QIcon(self.resource_path('feather/x.svg')))
        self.actionRaw_HTML.setIcon(QIcon(self.resource_path('feather/code.svg')))
        self.actionRendered_HTML.setIcon(QIcon(self.resource_path('feather/monitor.svg')))
        self.actionHighlight_Matches.setIcon(QIcon(self.resource_path('feather/edit-3.svg')))
        self.actionVisit_Help_Page.setIcon(QIcon(self.resource_path('feather/info.svg')))
        self.actionAbout.setIcon(QIcon(self.resource_path('feather/users.svg')))

        # _pages and _matched_pages will be in
        # the format {"URL": WebPage(URL)}
        self.pages = dict()
        self.matched_pages = dict()

        # Imported pages will be a list of URLs to crawl
        self._imported_pages = list()

        # An example of self._criteria would be
        # {'include': {'Firefox', 'Internet Explorer'}, 'ignore': {'Firefox 21.1'}, exclude: {'Google Chrome'}}
        self._criteria = {'include': set(), 'ignore': set(), "exclude": set()}

        # Initialize the format/appearance for
        # QTextBrowser's highlighting done in
        # self._highlight_matches
        self.highlight_format_green = QTextBlockFormat()
        self.highlight_format_green.setBackground(Qt.green)
        self.highlight_format_none = QTextBlockFormat()
        self.highlight_format_none.setBackground(Qt.transparent)

        # Link buttons
        self.pushButton_crawl.clicked.connect(self._crawl)
        self.pushButton_include.clicked.connect(self._add_inclusion_criteria)
        self.pushButton_ignore.clicked.connect(self._add_ignore_criteria)
        self.pushButton_exclude.clicked.connect(self._add_exclusion_criteria)
        self.pushButton_clear_criteria.clicked.connect(self._clear_criteria)
        self.pushButton_remove_criterion.clicked.connect(self._remove_criterion)

        # Link listWidgets
        self.listWidget_matched_pages.currentItemChanged.connect(self._update_browsers)

        # Link action menu items
        self.actionVisit_Help_Page.triggered.connect(self._open_help)
        self.actionAbout.triggered.connect(self._open_about_window)
        self.actionRaw_HTML.triggered.connect(self._switch_html_view)
        self.actionRendered_HTML.triggered.connect(self._switch_rendered_view)
        self.actionCrawl.triggered.connect(self._crawl)
        self.actionOpen_Page_in_Web_Browser.triggered.connect(self._open_web_page)
        self.actionClear_Criteria.triggered.connect(self._clear_criteria)
        self.actionReset_Crawled_Pages.triggered.connect(self._clear_pages)
        self.actionQuit.triggered.connect(self._quit)
        self.actionHighlight_Matches.triggered.connect(self._set_highlight_pages)
        self.actionExport.triggered.connect(self._activate_save_file_dialog)
        self.actionImport.triggered.connect(self._activate_open_file_dialog)

    def _set_status(self, status: str) -> None:
        """
        Set the bottom status bar message.
        """
        self.statusbar.showMessage(status)

    def _set_pages(self, pages: {str: WebPage}) -> None:
        """
        Set the pages attribute to a given dictionary
        of WebPage objects.
        """
        self.pages = pages
        self._update_pages()
        self._update_matched_pages_label();

    def _clear_pages(self):
        """
        Reset the crawled pages dictionary.
        """
        self.pages = dict()
        self._reset_browsers()
        self._update_pages()
        self._update_matched_pages_label()

    def _set_highlight_pages(self):
        """
        Switch self._highlight_pages on or off.
        """
        if self._highlight_pages:
            self._highlight_pages = False
            self._set_status("Highlighting matches set to OFF.")
        else:
            self._highlight_pages = True
            self._set_status("Highlighting matches set to ON.")
        self._update_browsers()

    def _stop_crawling(self, status: str) -> None:
        """
        Update the interface to stop crawling. This method
        is called if there's an exception within the
        crawling thread.
        """
        self._currently_crawling = False
        self.statusbar.showMessage(status)
        QApplication.restoreOverrideCursor()
        self._update_matched_pages_label()

    def _finish_crawling(self) -> None:
        """
        Update the matched pages list widget, announce that
        crawling is complete in the status bar, and restore
        the cursor.
        """
        self._currently_crawling = False
        self._update_pages()
        self._set_status(f'Finished crawling {self.lineEdit_url.text()}.')
        QApplication.restoreOverrideCursor()
        self._update_matched_pages_label()

        if len(self._imported_pages) > 0:
            self._create_crawler_thread(self._imported_pages.pop())

    def _update_pages(self) -> None:
        """
        Update the pages listWidget to reflect the WebPages
        within self.pages.
        """
        current_item = self.listWidget_matched_pages.currentIndex()
        self.listWidget_matched_pages.clear()
        if self._criteria != {'include': set(), 'ignore': set(), "exclude": set()}:
            for p in self.matched_pages:
                self.listWidget_matched_pages.addItem(p)
        else:
            for p in self.pages:
                self.listWidget_matched_pages.addItem(p)
        self.listWidget_matched_pages.setCurrentIndex(current_item)

    def _update_matched_pages_label(self) -> None:
        """
        Update the text label of matched pages to reflect the number
        of pages that are currently matched
        """
        if len(self._criteria['include']) > 0 or len(self._criteria['exclude']) > 0:
            self.label_matched_pages.setText(f"Matched Pages ({len(self.matched_pages)})")
        elif len(self.pages) > 0:
            self.label_matched_pages.setText(f"Matched Pages ({len(self.pages)})")
        else:
            self.label_matched_pages.setText(f"Matched Pages")

    def _update_criteria_display(self) -> None:
        """
        Update listWidget_search_criteria to display
        the current criteria populated in self._criteria.
        """
        self.listWidget_search_criteria.clear()
        for c in self._criteria:
            for k in self._criteria[c]:
                if c == 'include':
                    self.listWidget_search_criteria.addItem(f"Include : {k}")
                elif c == 'ignore':
                    self.listWidget_search_criteria.addItem(f"Ignore : {k}")
                elif c == 'exclude':
                    self.listWidget_search_criteria.addItem(f"Exclude : {k}")

    def _update_browsers(self) -> None:
        """
        Update both textBrowsers to display the contents
        of the currently selected WebPage within the
        matched pages listWidget.
        """
        if self.listWidget_matched_pages.currentItem():
            current_item = self.listWidget_matched_pages.currentItem().text()
            self.textBrowser_page_render.setText(self.pages[current_item].get_html())
            self.textBrowser_page_html.setPlainText(self.pages[current_item].get_html())
            self._highlight_matches()

    def _reset_browsers(self) -> None:
        """
        Reset both textBrowsers to display nothing.
        """
        self.textBrowser_page_html.setPlainText("")
        self.textBrowser_page_render.setText("")

    def _highlight_matches(self) -> None:
        """
        If there are currently plain text criteria
        within self._criteria, highlight any matches
        in the matched pages listWidget.
        """
        if not self._highlight_pages:
            return
        if len(self._criteria["include"]) == 0 and len(self._criteria["exclude"]) == 0:
            return

        for c in self._criteria["include"]:

            page = self.matched_pages[self.listWidget_matched_pages.currentItem().text()].get_html().splitlines()
            cursor = QTextCursor(self.textBrowser_page_html.document())
            iteration = -1

            # Since matched_pages already consists of pages containing
            # the criteria, it can be assumed that findBlockByLineNumber
            # will always work.
            for line in page:
                iteration += 1
                block = self.textBrowser_page_html.document().findBlockByLineNumber(iteration)
                block_pos = block.position()
                cursor.setPosition(block_pos)
                cursor.select(QTextCursor.LineUnderCursor)

                # It would be preferable if you didn't have to manually
                # format each block in white if it didn't contain the
                # text, and would probably save a lot of processing time -
                # especially on larger pages. That being said, if the else
                # clause does not explicitly say to format the block as none,
                # then PyQt won't format the matches as green.
                if c in line:
                    contains = False
                    for e in self._criteria["ignore"]:
                        if e in line:
                            contains = True
                            break
                    if not contains:
                        cursor.setBlockFormat(self.highlight_format_green)
                else:
                    cursor.setBlockFormat(self.highlight_format_none)

    def _create_crawler_thread(self, url: str) -> None:
        """
        Initialize a separate thread for crawling and
        connect all of the threads signals to
        their respective interface methods.
        """
        self.crawler_thread = CrawlerThread(url)
        self._set_status(f'Crawling {url} ...')
        self._currently_crawling = True
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.crawler_thread.signals.error.connect(self._stop_crawling)
        self.crawler_thread.signals.pages_crawled.connect(self._set_pages)
        self.crawler_thread.signals.finished.connect(self._finish_crawling)
        self.thread_pool.start(self.crawler_thread)

    def _crawl(self) -> None:
        """
        Check the lineEdit input for correctness, then
        initialize a crawler thread.
        """
        url = self.comboBox_schema.currentText() + self.lineEdit_url.text()

        if self._currently_crawling:
            self._set_status(f"Can't crawl website {url}, currently crawling another website.")
            return

        self._create_crawler_thread(url)

    def _crawl_from_file(self) -> None:
        """
        Prompt the user to open a .txt file and try to crawl
        each of the pages within that file.
        """
        path = QFileDialog.getOpenFileName(self, "Open web pages", filter="*.txt")
        try:
            if path[0] == '':
                return
            file = open(path[0], 'r')
            for i in file:
                self._imported_pages.append(i) if '\n' not in i else self._imported_pages.append(i[:-1])
            if len(self._imported_pages) > 0:
                self._create_crawler_thread(self._imported_pages.pop())
        except Exception as e:
            self._set_status(f"Couldn't open file {path[0]}, error: {e}")

    # In the future, depreciate these 3 separate methods into
    # one method.
    def _add_inclusion_criteria(self) -> None:
        """
        Add text from lineEdit_plain_text to the
        dictionary of search criteria to include.
        """
        if self.lineEdit_criterion.text() == "":
            self._set_status("Text criteria must be specified to be added.")
            return

        self._criteria["include"].add(self.lineEdit_criterion.text())
        self._update_criteria_display()
        self._match()
        self._update_pages()
        self._set_status(f"Added text \"{self.lineEdit_criterion.text()}\" to inclusion criteria.")
        self._reset_browsers()
        self.lineEdit_criterion.setText("")
        self._update_matched_pages_label()

    def _add_ignore_criteria(self) -> None:
        """
        Add text from lineEdit_plain_text to the
        dictionary of search criteria to ignore.
        """
        if self.lineEdit_criterion.text() == "":
            self._set_status("Text criteria must be specified to be added.")
            return

        self._criteria["ignore"].add(self.lineEdit_criterion.text())
        self._update_criteria_display()
        self._match()
        self._update_pages()
        self._set_status(f"Added text \"{self.lineEdit_criterion.text()}\" to ignoring criteria.")
        self._reset_browsers()
        self.lineEdit_criterion.setText("")
        self._update_matched_pages_label()

    def _add_exclusion_criteria(self) -> None:
        """
        Add text from lineEdit_plain_text to the
        dictionary of search criteria to exclude.
        """
        if self.lineEdit_criterion.text() == "":
            self._set_status("Text criteria must be specified to be added.")
            return

        self._criteria["exclude"].add(self.lineEdit_criterion.text())
        self._update_criteria_display()
        self._match()
        self._update_pages()
        self._set_status(f"Added text \"{self.lineEdit_criterion.text()}\" to exclusion criteria.")
        self._reset_browsers()
        self.lineEdit_criterion.setText("")
        self._update_matched_pages_label()

    def _clear_criteria(self) -> None:
        """
        Reset self._criteria and repopulate
        listWidget_search_criteria.
        """
        self._criteria = {'include': set(), 'ignore': set(), "exclude": set()}
        self._update_criteria_display()
        self._update_pages()
        self._reset_browsers()
        self._set_status("Cleared criteria.")

    def _remove_criterion(self) -> None:
        """
        Remove the current item selected from
        listWidget_search_criteria from self._criteria
        by generating indexes for each of the items
        in the listWidget using the same methodology
        as the _update_criteria_display method.
        """
        iteration_index = 0

        if self.listWidget_search_criteria.currentItem():
            current_item = self.listWidget_search_criteria.currentItem().text()
            if current_item[0:10] == "Include : ":
                self._criteria["include"].remove(current_item[10:])
                self._set_status(f"Removed criterion \"{current_item[10:]}\" from list of inclusion criteria.")
            elif current_item[0:9] == "Ignore : ":
                self._criteria["ignore"].remove(current_item[9:])
                self._set_status(f"Removed criterion \"{current_item[9:]}\" from list of ignoring criteria.")
            else:
                self._criteria["exclude"].remove(current_item[10:])
                self._set_status(f"Removed criterion \"{current_item[10:]}\" from list of exclusion criteria.")
        else:
            return

        self._match()
        self._update_criteria_display()
        self._update_pages()
        self._reset_browsers()
        self._update_matched_pages_label()

    def _match(self) -> None:
        """
        Refine self.matched_pages to only include
        pages from self.pages that satisfy the criteria
        added to self._criteria - in other words,
        generate self.matched_pages.
        """

        if self._criteria == {'include': set(), 'ignore': set(), 'exclude': set()}:
            return

        self.matched_pages = self.pages
        for k in self._criteria["include"]:
            self.matched_pages = has_text(self.matched_pages, k, self._criteria["ignore"])
        for k in self._criteria["exclude"]:
            self.matched_pages = does_not_have_text(self.matched_pages, k)
        self._update_pages()
        self._update_matched_pages_label()

    def _save_matched_pages(self) -> None:
        """
        Save the list of matched pages as a .txt file
        and open a file save dialog so the user can
        choose where to save the .txt file.
        """
        path = QFileDialog.getSaveFileName(self, "Save matched pages", filter="*.txt")
        try:
            if path[0] == '':
                return
            file = open(path[0], 'w')
            content = f"List of matched pages on {date.today()} using criteria {str(self._criteria)}\n\n"
            content += '\n'.join(self.matched_pages) if \
                len(self._criteria["include"]) > 0 or len(self._criteria["exclude"]) > 0 else '\n'.join(self.pages)
            file.write(content)
            file.close()
            self._set_status(f"Saved matched pages to {path[0]}.")
        except Exception as e:
            self._set_status(f"Couldn't save file to {path[0]}, error: {e}")

    # Action menu methods

    def _open_help(self) -> None:
        """
        Open a system web browser pointed to the help page.
        """
        open_new(self.HELP_URL)

    def _open_web_page(self) -> None:
        """
        Open a system web browser pointed to the currently
        selected web page from listWidget_matched_pages.
        """
        if self.listWidget_matched_pages.currentItem():
            open_new(self.listWidget_matched_pages.currentItem().text())

    def _open_about_window(self):
        """
        Open the About window
        """
        self.about_window.show()

    def _switch_html_view(self) -> None:
        """
        Make the raw HTML tab active within the tabWidget.
        """
        self.tabWidget_page.setCurrentIndex(0)

    def _switch_rendered_view(self) -> None:
        """
        Make the Rendered HTML tab active within the tabWidget.
        """
        self.tabWidget_page.setCurrentIndex(1)

    def _activate_save_file_dialog(self):
        """
        Activate a save file dialog to export a .txt file of
        matched pages.
        """
        self._save_matched_pages()
        
    def _activate_open_file_dialog(self):
        """
        Activate an open file dialog to open a .txt file of
        websites to crawl.
        """
        self._crawl_from_file()
