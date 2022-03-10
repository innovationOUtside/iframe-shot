# iframe-shot
IPython function to grab a screenshot of an IFrame cell output

Simple example:

```python

from iframe_shot import IFrameShot

# Generate an object with access to
# preloaded selenium powered headless browser
grabber = IFrameShot(True)

# HTML string
# TO DO - also allow an html file path
html = "<html><body><h1>hello there</h1></body></html>"

# Render HTML in browser and grab screenshot
grabber.getHTMLPNG(html)

# Returns rendered data-uri PNG of screenshotted html
# To save as png and return filenamem use:
# grabber.getHTMLPNG(html, embedded=False)
```


TO DO:

- also accept path to HTML file
- tidy up ad hoc tempfile handler for raw HTML
- handle requirements, webdriver setup etc
