from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC

from anubis.page_object_utils.decorators import wait_for_page_to_load


# getters
def get_element(driver, by_locator: tuple, **kwargs):
    return driver.find_element(*by_locator)


def get_elements(driver, by_locator: tuple, **kwargs):
    return driver.find_elements(*by_locator)


def get_element_attribute(driver, by_locator: tuple, attribute: str, **kwargs) -> str:
    return driver.find_element(*by_locator).get_attribute(attribute.lower())


def get_element_text(driver, by_locator: tuple, **kwargs) -> str:
    return driver.find_element(*by_locator).text


# clicks
@wait_for_page_to_load
def click(driver, by_locator: tuple, **kwargs) -> None:
    # locate and move to the element
    element = WDW(driver, 3.14).until(EC.visibility_of_element_located(by_locator))

    scroll_height = driver.execute_script('return document.body.scrollHeight')
    window_size = driver.get_window_size()['height']

    if element.location['y'] > (scroll_height - .5 * window_size):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    elif element.location['y'] < (.5 * window_size):
        driver.execute_script('window.scrollTo(0, 0)')
    elif not element.is_displayed():
        driver.execute_script(
            f"window.scrollTo({element.location['x']}, {element.location['y'] - .5 * window_size});")

    # wait for element to be clickable, then click it
    WDW(driver, 3.14).until(EC.element_to_be_clickable(by_locator)).click()


def click_element_by_offset(driver, by_locator: tuple, x_off: int, y_off: int, **kwargs) -> None:
    element = get_element(driver, by_locator)
    ActionChains(driver).move_to_element_with_offset(element, x_off, y_off).click().perform()


def drag_element_by_offset(driver, by_locator: tuple, x_off: int, y_off: int, **kwargs) -> None:
    element = get_element(driver, by_locator)
    ActionChains(driver).click_and_hold(element).move_by_offset(x_off, y_off).perform()


def click_if_valid(driver, valid_item_map: dict, item_name: str, **kwargs) -> None:
    if item_name.lower() in valid_item_map:
        click(driver, valid_item_map[item_name.lower()])
    else:
        print(f'You tried to click an item called <{item_name}>')
        print(f'Make sure to select from the following:\n{list(valid_item_map.keys())}')


# visibility
@wait_for_page_to_load
def wait_until_visible(driver, by_locator: tuple, **kwargs):
    WDW(driver, 3.14).until(EC.visibility_of_element_located(by_locator))


@wait_for_page_to_load
def wait_until_invisible(driver, by_locator: tuple, **kwargs):
    WDW(driver, 3.14).until(EC.invisibility_of_element_located(by_locator))


@wait_for_page_to_load
def is_visible(driver, by_locator: tuple, **kwargs) -> bool:
    try:
        element = WDW(driver, 3.14).until(EC.visibility_of_element_located(by_locator))
        return element.is_displayed()
    except Exception as e:
        return False


# other
def enter_text(driver, by_locator: tuple, text, **kwargs):
    return WDW(driver, 3.14).until(EC.visibility_of_element_located(by_locator)).send_keys(text)


def hover_to(driver, by_locator: tuple, **kwargs) -> None:
        el = WDW(driver, 3.14).until(EC.visibility_of_element_located(by_locator))
        window_size = driver.get_window_size()['height']

        driver.execute_script(f"window.scrollTo({el.location['x']}, {el.location['y'] - .5 * window_size});")
        ActionChains(driver).move_to_element(el).perform()


def highlight_element(driver, by_locator: tuple, **kwargs) -> None:
    el = driver.find_element(*by_locator)
    driver.execute_script('arguments[0].setAttribute("style", "background: yellow; border: 2px solid red;");', el)
