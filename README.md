# iframe-shot
IPython function to grab a screenshot of an IFrame cell output

Simple example:

```python

from iframe_shot import IFrameShot

# Generate an object with access to
# preloaded selenium powered headless browser
grabber = IFrameShot(True)

# HTML string
html = "<html><body><h1>hello there</h1></body></html>"

# Render HTML in browser and grab screenshot
grabber.getHTMLPNG(html)

# Returns rendered data-uri PNG of screenshotted html
# To save as png and return filenamem use:
# grabber.getHTMLPNG(html, embedded=False)
```

As well as passing in a raw HTML string, we can also path in a path to an HTML file or an object with a `_repr_html_()` function.

Passing a filename via `html_out=FILENAME` will write the HTML that was rendered to that file.

Passing a filename via `png_out=FILENAME` will write the image out to a file of that name.

Setting `embedded=True` will return an `IPython.display.HTML()` wrapped image tag containing a data URI. Setting `embedded=False` will return an image tag pointing to a local file.

Setting `quiet=False` will suppress the return of any displayabe output image.


TO DO:

- handle requirements, webdriver setup etc
