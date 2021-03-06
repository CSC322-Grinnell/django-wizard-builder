import logging
import os
from datetime import datetime
from distutils.util import strtobool
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from django.contrib.sites.models import Site
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps'
)
logger = logging.getLogger(__name__)


class Assertions(object):

    def assertCss(self, css):
        self.assertTrue(
            self.browser.find_elements_by_css_selector(css),
        )

    def assertSelectorContains(self, css, text):
        assertion_valid = False
        elements = list(self.browser.find_elements_by_css_selector(css)),
        elements = elements[0]
        element_text = ''
        for element in elements:
            element_text += element.text
            if text in element.text:
                assertion_valid = True
        if not assertion_valid:
            raise AssertionError('''
                '{}' not found in '{}'
            '''.format(text, element_text))


class FunctionalTest(Assertions, StaticLiveServerTestCase):

    fixtures = [
        'wizard_builder_data',
    ]

    def setUp(self):
        super().setUp()
        port = urlparse(self.live_server_url).port
        Site.objects.filter(id=1).update(domain='localhost:{}'.format(port))
        self.browser.get(self.live_server_url)
        self.wait_for_until_body_loaded()

    @classmethod
    def setUpClass(cls):
        super(FunctionalTest, cls).setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-gpu")
        cls.browser = webdriver.Chrome(
            chrome_options=chrome_options,
        )

    @classmethod
    def tearDownClass(cls):
        try:
            cls.browser.quit()
        except (AttributeError, OSError):
            pass  # brower has already been quit!
        super(FunctionalTest, cls).tearDownClass()

    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.browser.window_handles):
                self._windowid = ix
                self.browser.switch_to.window(handle)
                self._take_screenshot()
                self._dump_html()
        super(FunctionalTest, self).tearDown()

    def wait_for_until_body_loaded(self):
        WebDriverWait(self.browser, 3).until(
            lambda driver: driver.find_element_by_tag_name('body'),
        )

    def _test_has_failed(self):
        try:
            for method, error in self._outcome.errors:
                if error:
                    return True
        except AttributeError:
            pass  # not all python versions has access to self._outcome
        return False

    def _take_screenshot(self):
        filename = self._get_filename() + '.png'
        logger.info('screenshotting to {}'.format(filename))
        self.browser.get_screenshot_as_file(filename)

    def _dump_html(self):
        filename = self._get_filename() + '.html'
        logger.info('dumping page HTML to {}'.format(filename))
        with open(filename, 'w') as f:
            f.write(self.browser.page_source)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(':', '.')[:19]
        return '{folder}/{classname}.{method}-window{windowid}-{timestamp}'.format(
            folder=SCREEN_DUMP_LOCATION,
            classname=self.__class__.__name__,
            method=self._testMethodName,
            windowid=self._windowid,
            timestamp=timestamp)
