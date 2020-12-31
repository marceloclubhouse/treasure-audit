# Treasure Audit
### A simple web spider with a desktop interface

Treasure Audit is a multi-platform desktop Web spider that allows users to crawl and search websites, without having to worry about out-of-date content as a result of caching.

## Features
- Import a list of websites to crawl from a .txt file
- Export a list of matched pages
- Add a virtually unlimited amount of matching criteria to filter for content
- View pages with an HTML text viewer or HTML renderer
- Highlight matches within the HTML view
- Flexible interface optimized for webmasters and people building out sites
- Real-time auditing – no more caching from Google
- Linux, Mac, and Windows compatibility

## Binaries
You can download the compiled binaries from GitHub for Linux, Mac, and Windows: https://github.com/marceloclubhouse/treasure-audit/releases/tag/v0.1.2

## Manual Installation
Download and install Python from
```
https://www.python.org/downloads/
```
Install Requests, BeautifulSoup, and PyQt5
```
pip3 install requests bs4 pyqt5
```
Download Treasure Audit from this page and execute ```run.py```
```
python3 run.py
```

## Usage
Choose a schema and enter the URL of the website you want to crawl then click Crawl

<p align="center">
  <img src="https://raw.githubusercontent.com/marceloclubhouse/treasure-audit/master/images/Screenshot%20from%202020-07-24%2014-33-43.png">
</p>

Add your criteria to narrow down the list of matched pages.

<p align="center">
  <img src="https://raw.githubusercontent.com/marceloclubhouse/treasure-audit/master/images/Screenshot%20from%202020-07-24%2014-37-11.png">
</p>

After the pages are crawled, you can click on the individual pages to view their HTML, or you can choose to render the pages in a boxed web browser (without any assets like CSS, JS, or images)

<p align="center">
  <img src="https://raw.githubusercontent.com/marceloclubhouse/treasure-audit/master/images/Screenshot%20from%202020-07-24%2014-37-56.png">
</p>

If you want to see where your criteria matches within the HTML, you can enable highlighting by going to View > Highlight Matches, which will highlight your matches in green within the HTML viewer.

<p align="center">
  <img src="https://raw.githubusercontent.com/marceloclubhouse/treasure-audit/master/images/Screen-Shot-2020-07-17-at-1.27.20-PM.png">
</p>

At which point you can scroll through the HTML viewer to find the match.

<p align="center">
  <img src="https://raw.githubusercontent.com/marceloclubhouse/treasure-audit/master/images/Screenshot%20from%202020-07-24%2014-41-40.png">
</p>

If you find a match that you don’t want to include, you can copy and paste it into the criterion box and choose to ignore it

<p align="center">
  <img src="https://raw.githubusercontent.com/marceloclubhouse/treasure-audit/master/images/Screenshot%20from%202020-07-24%2014-42-58.png">
</p>
You can open the page you’re viewing in an external web browser by either going to Menu > Edit > Open Page in Web Browser
<p align="center">
  <img src="https://raw.githubusercontent.com/marceloclubhouse/treasure-audit/master/images/Screen-Shot-2020-07-17-at-1.29.54-PM.png">
</p>

which will open the page in your default browser.

<p align="center">
  <img src="https://raw.githubusercontent.com/marceloclubhouse/treasure-audit/master/images/Screen-Shot-2020-07-17-at-1.31.24-PM-1024x505.png">
</p>

## Credits
- Logo – Shamash Teran
- Icons – Cole Bemis
- GUI and Software – Marcelo Cubillos

Treasure Audit is provided under the GPL v3 License. See LICENSE.txt for more information.
