import os
import time
from selenium import webdriver
import tempfile
import mimetypes
import base64
from IPython.display import Image, HTML
from pathlib import Path
from urllib import request
import uuid
from importlib.util import find_spec

class IFrameShot:
    def __init__(self, init=False, scale_factor=2, quiet=False,
                headless=True, browser_type='firefox'):
        self.browser = None
        self.headless = headless
        self.scale_factor = scale_factor
        self.quiet = quiet
        self.browser_type = browser_type
        self.raw = None
        self.mimetype = None
        if init:
            self.init_browser()

    def __del__(self):
        if self.browser is not None:
            self.browser.quit()    
    
    # Should we allow support different browsers for the screengrabs?
    # # eg Firefox as well as Chrome? OR is `force-device-scale-factor` chrome only (or maybe there is a Firefox equivalent?) What does it do, anyway?
    def init_browser(self):
        if self.browser_type=='chrome':
            opt = webdriver.ChromeOptions()
            opt.add_argument('--force-device-scale-factor={}'.format(self.scale_factor))
            if self.headless:
                opt.add_argument('headless')

            self.browser = webdriver.Chrome(options=opt)
            
        elif self.browser_type=='firefox':
            #print('using firefox')
            from selenium.webdriver.firefox.options import Options

            opt = Options()
            if self.headless:
                opt.headless = True

            self.browser = webdriver.Firefox(options=opt)

    #Via https://stackoverflow.com/a/52572919/454773
    def get_screenshot(self, driver,path):
        # Ref: https://stackoverflow.com/a/52572919/
        original_size = driver.get_window_size()
        required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
        required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
        driver.set_window_size(required_width, required_height)
        # driver.save_screenshot(path)  # has scrollbar
        driver.find_element_by_tag_name('body').screenshot(path)  # avoids scrollbar
        driver.set_window_size(original_size['width'], original_size['height'])

    def _get_repr_html(self, obj):
        """If available, return _repr_html_ html string from object"""
        if hasattr(obj, "_repr_html_") and callable(getattr(obj, "_repr_html_")):
            return obj._repr_html_()
        return obj

    def data_uri(self):
        """Return data URI. """
        prefix = f'data:image/{self.mime};base64,'
        data_uri = prefix + self.raw
        return data_uri

    def img_tag(self):
        """Return HTML image tag."""
        return f'<img src="{self.data_uri()}" />'

    def img_path_to_raw(self, path):
        """Get raw data from image; image location provided by path."""
        with open(path, 'rb') as f:
            img = f.read()

        self.mime, _ = mimetypes.guess_type(path)
        self.raw = base64.b64encode(img).decode('utf-8')
            

    def captureImage(self, url, delay=None, scale_factor=2,
                    height=420, width=800):
        ''' Render HTML file in browser and grab a screenshot. '''
        
        #options = Options()
        #options.headless = True

        if self.browser is None:
            self.init_browser(scale_factor=scale_factor)
            reset_browser = True
        else:
            reset_browser = False

        #browser.set_window_size(width, height)
        self.browser.get(url)
        #Should really do this with some sort of browser onload check
        if delay is not None:
            time.sleep(delay)

        fp_png = tempfile.NamedTemporaryFile(suffix='.png')
        self.get_screenshot(self.browser, fp_png.name)
      
        self.img_path_to_raw(fp_png.name)
        fp_png.close()
    
        if reset_browser:
            self.browser.quit()

    def img(self):
        """Return data URI as via IPython.display.Image"""
        return HTML(self.img_tag())

    def set_quiet(self, quiet=False):
        self.quiet = quiet

    # Create a function that accepts some HTML, opens it in a browser,
    # grabs a screenshot, saves image and returns filepath to image.
    def getHTMLPNG(self, html, html_out=None, png_out=None,
                     scale_factor=2, embedded=True):
        ''' Save HTML as file.
            Pass an HTML string, url, filepath or file object.'''

        # Have we been passed a string?
        if isinstance(html, str):
            # Is it likely a URL?
            if html.startswith("http"):
                # If so, download it and get the HTML
                html = request.urlopen(html).read().decode('utf8')
            # or perhaps a local file? 
            elif Path(html).is_file():
                html = Path(html).read_text()
            else:
                # Assume it's HTML
                html = html

        else:
            # Or do we have an object which has a _repr_html_ method?
            # For pandas, see if we have a pandas style object
            # or an object with a to_html() method.
            # For an unstyled dataframe, we are missing the notebook stylesheet
            try:
                if hasattr(html, "style"):
                    html = html.style.to_html()
                else:
                    # Maybe we were passed a styler object
                    # or a series/dataframe?
                    html = html.to_html()
            except:
                # Is there a _repr_html_?
                html = self._get_repr_html(html)

        # If there appears to be no HTML, give up now
        if not html:
            return

        # If we were given an HTML output filename, use it
        if html_out:
            fn = Path(html_out).resolve()
        else:
            # Create a (temporary) unique filename
            fn = Path(f'{str(uuid.uuid4())}.html').resolve()

        # Write the HTML to the file
        with open(fn, 'w') as out:
            out.write(html)

        # Get a file:// path we can use as a browser URL
        tmpurl = f'file://{fn}'

        # Load the file into the automated browser and grab a screenshot
        self.captureImage(tmpurl, scale_factor=scale_factor)

        # If we created the temporary html file, delete it
        if not html_out:
            fn.unlink()

        # If we aren't embedding the image, return the filepath
        if not embedded or png_out:
            if png_out:
                fn = png_out
            else:
                # Create a (temporary) unique filename
                fn = f'{str(uuid.uuid4())}.png'

            with open(fn, 'wb') as out:
                out.write(base64.b64decode(self.raw))

            if not embedded:
                return HTML(f'<img src="{fn}" />')

        # If we're not being quiet, return the image
        if not self.quiet:
            return self.img()
