import os
import time
from selenium import webdriver
import tempfile
import mimetypes
import base64
from IPython.display import Image, HTML

class IFrameShot:
    def __init__(self, init=False, scale_factor=2,
                headless=True, browser_type='firefox'):
        self.browser = None
        self.headless = headless
        self.scale_factor = scale_factor
        self.browser_type = browser_type
        self.raw = None
        self.mimetype = None
        if init:
            self.init_browser()
            
    
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
                    height=420, width=800,
                    logging=False, save=True):
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


    # Create a function that accepts some HTML, opens it in a browser,
    # grabs a screenshot, saves image and returns filepath to image.
    def getHTMLPNG(self, html, basepath='.', path='testpng',
                    fnstub='testhtml', scale_factor=2, embedded=True):
        ''' Save HTML as file. '''
        # We should really pop the HTML in a temporary file
        if not os.path.exists(path):
            os.makedirs('{}/{}'.format(basepath, path))
        fn= f'{os.getcwd()}/{basepath}/{path}/{fnstub}.html'

        with open(fn, 'w') as out:
            out.write(html)

        tmpurl = f'file://{fn}'
        self.captureImage(tmpurl, scale_factor=scale_factor)
        os.remove(fn)
        
        if not embedded:
            fn= f'{os.getcwd()}/{basepath}/{path}/{fnstub}.png'
            with open(fn, 'wb') as out:
                out.write(base64.b64decode(self.raw))
                return fn
        return self.img()
