from selenium.webdriver.support.ui import WebDriverWait as WDW
from functools import wraps
import importlib
import time
from inspect import getfullargspec


def handle_locator(function):
    """
    This wraps a function that takes a locator, an arbitrary number of args, and an arbitrary number of kwargs.
    If the locator length is greater than 2, it assumes the tuple contains page object data and sets the page.
    If there are kwargs, it assumes they must be used to format the locator string and handles the interpolation.
    Finally, it runs the function.
    """
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        locator = args[0]
        page_object_location = None

        # separate the locator from the new page
        if len(locator) == 3:
            page_object_location = locator[2]
            locator = locator[:2]

        # interpolate values into locator string if necessary
        locator = (locator[0], locator[1].format_map(kwargs))

        # perform the wrapped function
        function_call = function(self, locator, *args[1:], **kwargs)

        # if new page, update the `current_page` attribute of the the context object
        if '.click' in function.__repr__() and page_object_location:
            WDW(self.driver, 10).until(lambda _: self.driver.execute_script('return document.readyState') == 'complete')
            page_object = importlib.import_module(f'page_objects.{page_object_location}', 'Page')
            if hasattr(self.context, 'current_page'):
                self.context.current_page = getattr(page_object, 'Page')(self.context)
            elif hasattr(self.context, 'page'):
                self.context.page = getattr(page_object, 'Page')(self.context)
            time.sleep(3)   # this allows enough time for the page to load
        return function_call
    return wrapper


def wait_for_page_to_load(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        argspec = getfullargspec(function)
        driver = args[argspec.args.index('driver')]
        try:
            WDW(driver, 10).until(lambda _: driver.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            print(e)

        return function(*args, **kwargs)
    return wrapper
