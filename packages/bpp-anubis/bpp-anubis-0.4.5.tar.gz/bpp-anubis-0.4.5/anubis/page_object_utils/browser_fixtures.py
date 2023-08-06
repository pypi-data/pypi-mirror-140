from behave import fixture
from selenium.webdriver import Chrome, ChromeOptions, Safari, FirefoxOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging

# drivers
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

super_logger = logging.getLogger('ROOT')


@fixture
def chrome(context):
    # setup chrome options
    options = ChromeOptions()
    options.add_argument('--ignore-certificate-errors')

    if context.config.userdata['headless'].lower() == 'true':
        options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--verbose')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    context.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options, desired_capabilities=caps)
    # add auth cookie to browser
    # context.driver.add_cookie({
    #     'domain': context.env_data['domain'],
    #     'name':   context.env_data['cookie_name'],
    #     'value':  context.env_data['token']
    # })
    if hasattr(context, 'composite_request'):
        context.driver.get(context.composite_request.url)
    else:
        context.driver.get(context.env_data['base_url'])

    context.driver.maximize_window()
    yield context.driver
    context.driver.quit()


@fixture
def safari(context):
    context.driver = Safari()
    yield context.driver
    context.driver.quit()


@fixture
def firefox(context):
    ff_options = FirefoxOptions()
    if context.config.userdata['headless'].lower() == 'true':
        ff_options.headless = True
    context.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=ff_options, service_log_path='/dev/null')  # todo - hard-coded `service_log_path` = probably problematic
    context.driver.maximize_window()
    context.driver.get(context.composite_request.url)
    yield context.driver
    context.driver.quit()
