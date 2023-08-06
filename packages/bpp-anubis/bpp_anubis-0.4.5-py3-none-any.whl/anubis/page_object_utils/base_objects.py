# selenium dependencies
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC

# custom dependencies
from anubis.page_object_utils.decorators import handle_locator
from anubis.page_object_utils import _shared_driver_functions


class BasePage:
    def __init__(self, context):
        self.context = context
        self.driver: webdriver = context.driver
        self.url = context.env_data['base_url']

    # <editor-fold> desc="Simple browser controls ...">
    def nav_to_url(self, url: str) -> None:
        self.driver.get(url)

    def refresh(self) -> None:
        self.driver.refresh()

    def go_back(self) -> None:
        self.driver.back()

    def go_forward(self) -> None:
        self.driver.forward()

    def scroll_top(self) -> None:
        self.driver.execute_script('window.scrollTo(0, 0)')

    def scroll_bottom(self) -> None:
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')

    def shut_down(self) -> None:
        self.driver.close()
        self.driver.quit()

    def switch_to_tab_by_position(self, position: int) -> None:
        self.driver.switch_to.window(self.driver.window_handles[position])

    def close_tab_by_position(self, position: int) -> None:
        raise NotImplementedError
    # </editor-fold>

    # <editor-fold> desc="Getters ...">
    @handle_locator
    def get_element(self, by_locator: tuple, **kwargs) -> WebElement:
        return _shared_driver_functions.get_element(self.driver, by_locator, **kwargs)

    @handle_locator
    def get_elements(self, by_locator: tuple, **kwargs) -> list:
        return _shared_driver_functions.get_elements(self.driver, by_locator, **kwargs)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_current_title(self) -> str:
        return self.driver.title

    @handle_locator
    def get_element_attribute(self, by_locator: tuple, attribute: str, **kwargs) -> str:
        return _shared_driver_functions.get_element_attribute(self.driver, by_locator, attribute, **kwargs)

    @handle_locator
    def get_element_text(self, by_locator: tuple, **kwargs) -> str:
        return _shared_driver_functions.get_element_text(self.driver, by_locator, **kwargs)
    # </editor-fold>

    # <editor-fold> desc="Visibility ...">
    @handle_locator # todo - check
    def is_visible(self, by_locator: tuple, **kwargs) -> bool:
        return _shared_driver_functions.is_visible(self.driver, by_locator, **kwargs)

    @handle_locator # todo - check
    def wait_until_visible(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.wait_until_visible(by_locator, **kwargs)

    @handle_locator # todo - check
    def wait_until_invisible(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.wait_until_invisible(by_locator, **kwargs)

    def wait_for_page_to_load(self) -> None:
        try:
            WDW(self.driver, 10).until(lambda _: self.driver.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            print(e)
    # </editor-fold>

    # <editor-fold desc="Element Interactions ...">
    @handle_locator
    def drag_element_by_offset(self, by_locator: tuple, x_offset: int, y_offset: int, **kwargs) -> None:
        return _shared_driver_functions.drag_element_by_offset(self.driver, by_locator, x_offset, y_offset, **kwargs)

    @handle_locator
    def click_element_by_offset(self, by_locator: tuple, x_offset: int, y_offset: int, **kwargs) -> None:
        return _shared_driver_functions.click_element_by_offset(self.driver, by_locator, x_offset, y_offset, **kwargs)

    @handle_locator
    def click(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.click(self.driver, by_locator, **kwargs)

    @handle_locator
    def enter_text(self, by_locator: tuple, text: str, **kwargs) -> None:
        return _shared_driver_functions.enter_text(self.driver, by_locator, text, **kwargs)

    @handle_locator
    def hover_to(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.hover_to(self.driver, by_locator, **kwargs)

    @handle_locator
    def highlight_element(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.highlight_element(self.driver, by_locator, **kwargs)
    # </editor-fold>


class BaseModal:
    def __init__(self, context):
        self.context = context
        self.driver = context.driver
        self.locators = None

    @handle_locator
    def click(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.click(self.driver, by_locator, **kwargs)

    def close(self):
        if hasattr(self.locators, 'close_button'):
            self.click(self.locators.close_button)
        else:
            print('Could not find "close_button" locator')

    def confirm(self):
        if hasattr(self.locators, 'confirm'):
            self.click(self.locators.confirm)
        elif hasattr(self.locators, 'okay'):
            self.click(self.locators.okay)
        else:
            print('Could not find okay/confirm locator')

    @handle_locator
    def get_element(self, by_locator: tuple, **kwargs) -> WebElement:
        return _shared_driver_functions.get_element(self.driver, by_locator, **kwargs)

    @handle_locator
    def get_elements(self, by_locator: tuple, **kwargs) -> list:
        return _shared_driver_functions.get_elements(self.driver, by_locator, **kwargs)

    @handle_locator
    def enter_text(self, by_locator: tuple, text: str, **kwargs) -> None:
        return _shared_driver_functions.enter_text(self.driver, by_locator, text, **kwargs)

    @handle_locator
    def hover_to(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.hover_to(self.driver, by_locator, **kwargs)

    def modal_is_displayed(self):
        try:
            element = WDW(self.driver, 3).until(EC.visibility_of_element_located(self.locators.modal))
            return True
        except:
            return False

    @handle_locator
    def wait_until_visible(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.wait_until_visible(by_locator, **kwargs)

    @handle_locator
    def wait_until_invisible(self, by_locator: tuple, **kwargs) -> None:
        return _shared_driver_functions.wait_until_invisible(by_locator, **kwargs)

    @handle_locator
    def click_element_by_offset(self, by_locator: tuple, x_offset: int, y_offset: int, **kwargs) -> None:
        return _shared_driver_functions.click_element_by_offset(self.driver, by_locator, x_offset, y_offset, **kwargs)


class BaseLocator:
    def __add__(self, other):
        combination = {}
        combination.update(self.__dict__)
        combination.update(other.__dict__)
        new = self.__class__()
        new.__dict__.update(combination)
        return new

    def __iadd__(self, other):
        combination = {}
        combination.update(self.__dict__)
        combination.update(other.__dict__)
        new = self.__class__()
        new.__dict__.update(combination)
        return new
