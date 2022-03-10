# iframe-shot
IPython function to grab a screenshot of an IFrame cell output

Simple example:

```python

from iframe_shot import IFrameShot

grabber = IFrameShot(True)
html = "<html><body><h1>hello there</h1></body></html>"
grabber.getHTMLPNG(html)

# Returns rendered data-uri PNG of screenshotted html
# To save as png and return filenamem use:
# grabber.getHTMLPNG(html, embedded=False)
```


TO DO:

- also accept path to HTML file
- tidy up ad hoc tempfile handler for raw HTML
