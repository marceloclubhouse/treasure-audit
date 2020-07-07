"""
Treasure Audit - auditor.py

Auditor contains script that can crawl a website and
return a set of pages that represent the publicly-accessible
content of said website. There is also script to sift
through the set of pages for content and return a set of
matching pages.

Revisions:
- 2020/06/15 : First revision
- 2020/07/07 : Added does_not_have_text() function

Copyright (C) 2020 Marcelo Cubillos
This software is licensed under the GPL v3, see LICENSE.txt
for more information.
"""

import requests
import re
from bs4 import BeautifulSoup


class WebPage:
    """
    A WebPage object is represented by a URL and contains the HTML
    content of that URL. Attributes can be accessed through a
    WebPage object's methods:
    
    URL -> get_url() -> str
    HTML -> get_html() -> str
    LINKS -> get_links() -> {str}
    INTERNAL LINKS -> get_internal_links() -> {str}
    
    The WebPage class also includes a regex pattern that allows
    the WebPage URL to be parsed into schema, domain, page, and
    file extension.
    """

    URL_REGEX = re.compile("^(?P<schema>http:\/\/|https:\/\/)?"
                           "(?P<domain>[a-z|0-9|\.]+\.[a-z]+)?"
                           "(?P<page>(?:\/[A-z|0-9|\-|_|~|:|?|[|\]|@|!|$|&|'|(|)|\*|\+|,|;|=]+)*)"
                           "(?:(?P<extension>\.[a-z]+)|\/)?$")

    def __init__(self, url: str):

        assert re.match(WebPage.URL_REGEX, url), f"'WebPage' must be created with valid URL, got {url}."
        assert re.match(WebPage.URL_REGEX, url), f"'WebPage' object must have valid domain, got {url}."

        # Retrieve the HTML of a web page
        page = requests.get(url).content
        self.soup = BeautifulSoup(page, 'html.parser')

        self._url = url
        self.domain = re.match(WebPage.URL_REGEX, self._url)['domain']
        self.page = re.match(WebPage.URL_REGEX, self._url)['page']

        # Add each anchor (<a>) tag within the page
        # to the object's set of links if the anchor
        # has a href value.
        self._links = set()
        for a in self.soup.find_all('a'):
            if 'href' in a.attrs:
                self._links.add(a['href'])

        self._internal_links = WebPage.internal_links(self._links, self.domain)
        self._html_content = self.soup.prettify()

    def __repr__(self):
        return f"WebPage({self._url})"

    def __str__(self):
        return self._url

    def __eq__(self, other):
        if type(other) == WebPage:
            if other.domain == self.domain and other.page == self.page:
                return True
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not WebPage.__eq__(self, other)

    def __hash__(self):
        return hash((self.domain, self.page))

    def get_url(self) -> str:
        """
        Return the URL of WebPage object
        """
        return self._url

    def get_html(self) -> str:
        """
        Return HTML contents of WebPage object
        """
        return self._html_content

    def get_links(self) -> {str}:
        """
        Return set of all links within WebPage object
        """
        return self._links

    def get_internal_links(self) -> {str: 'WebPage'}:
        """
        Return a set of all of the internal links within the WebPage Object
        """
        return self._internal_links

    @staticmethod
    def internal_links(links: {str}, domain: str) -> {str}:
        """
        Given a set of URL's and a domain string, return a
        set of URL's that are within the specified domain
        """

        internal_links = set()

        # Remove / from the end of domain if necessary
        if domain[-1] == '/':
            domain = domain[:-1]

        # Add all links that are within the domain to
        # internal links
        for l in links:
            match = re.match(WebPage.URL_REGEX, l)
            if match is not None and match['extension'] is None:

                # If the URL has the domain in it
                # e.g. url = www.a.com && link = www.a.com/b
                if match['domain'] == domain:
                    internal_links.add(l)

                # Or if the link is an implicit internal
                # link, e.g. /clubhouse/games
                elif match['domain'] is None:
                    internal_links.add('http://' + domain + match['page'])

        return internal_links


def find_all_pages(current_page: WebPage, traversed_pages=dict()) -> {str: WebPage}:
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
                traversed_pages.update(find_all_pages(WebPage(p), traversed_pages))
            except Exception as e:
                print(f"Error crawling {p}: {e}")

    return traversed_pages


def has_element(web_pages: {str: WebPage}, container: str) -> {str: WebPage}:
    """
    Given a dictionary of WebPages and element attributes,
    return another dictionary of WebPages that contain the
    specified elements.
    """
    new_dict = dict()
    for w in web_pages:
        if web_pages[w].soup.find_all(container):
            new_dict[w] = web_pages[w]
    return new_dict


def has_text(web_pages: {str: WebPage}, text: str) -> {str: WebPage}:
    """
    Given a dictionary of WebPages and a search term,
    return another dictionary of WebPages that contain
    the specified text within them.
    """
    new_dict = dict()
    for w in web_pages:
        for line in web_pages[w].get_html().splitlines():
            if text in line:
                new_dict[w] = web_pages[w]
                break
    return new_dict


def does_not_have_text(web_pages: {str: WebPage}, text: str) -> {str: WebPage}:
    """
    Given a dictionary of WebPages and a search term,
    return another dictionary of WebPages in which
    no pages contain that search term.
    """
    new_dict = dict()
    for w in web_pages:
        contains = False
        for line in web_pages[w].get_html().splitlines():
            if text in line:
                contains = True
                break
        if not contains:
            new_dict[w] = web_pages[w]
    return new_dict


if __name__ == '__main__':
    pass
