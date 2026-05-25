"""
dynamic_page.py — Page Object для тестирования AJAX-контента.

Тестовый сайт: https://the-internet.herokuapp.com
  - /dynamic_loading/1  — элемент скрыт в DOM, появляется после клика
  - /dynamic_loading/2  — элемент рендерится в DOM только после AJAX
  - /dynamic_controls   — чекбокс и текстовое поле добавляются/удаляются
  - /ajax_data_sets     — таблица загружается через AJAX (внешний сайт)

Принцип работы Explicit Wait:
  1. Вызов WebDriverWait(driver, timeout)
  2. Указание условия из expected_conditions (EC)
  3. Selenium опрашивает DOM каждые 0.5 сек пока:
       а) условие выполнится → возвращает элемент
       б) истечёт timeout → выбрасывает TimeoutException
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class DynamicLoadingPage(BasePage):
    """
    Страница /dynamic_loading/1 и /dynamic_loading/2.
    Кнопка Start запускает «загрузку», после которой
    появляется надпись Hello World!
    """

    BASE_URL = "https://the-internet.herokuapp.com/dynamic_loading"

    # Локаторы (хранятся в классе — принцип POM)
    START_BUTTON   = (By.CSS_SELECTOR, "#start button")
    LOADING_BAR    = (By.ID, "loading")
    FINISH_TEXT    = (By.CSS_SELECTOR, "#finish h4")

    def open_example(self, example_num: int):
        """Открыть пример 1 или 2."""
        self.open(f"{self.BASE_URL}/{example_num}")

    def click_start(self):
        """Нажать кнопку Start."""
        self.click(self.START_BUTTON)

    def wait_for_loading_to_finish(self):
        """
        Ждём: сначала появляется лоадер, потом он исчезает.
        Это классический паттерн для AJAX-индикаторов.
        """
        # Ждём появления прогресс-бара
        self.wait_present(self.LOADING_BAR)
        # Ждём его исчезновения (AJAX завершился)
        self.wait_invisible(self.LOADING_BAR)

    def get_result_text(self) -> str:
        """Получить текст результата после загрузки."""
        return self.get_text(self.FINISH_TEXT)


class DynamicControlsPage(BasePage):
    """
    Страница /dynamic_controls.
    Тестирует добавление/удаление элементов через AJAX:
      - кнопка Remove/Add для чекбокса
      - кнопка Enable/Disable для текстового поля
    """

    URL = "https://the-internet.herokuapp.com/dynamic_controls"

    CHECKBOX        = (By.CSS_SELECTOR, "#checkbox input")
    REMOVE_ADD_BTN  = (By.CSS_SELECTOR, "#checkbox-example button")
    ENABLE_DISABLE_BTN = (By.CSS_SELECTOR, "#input-example button")
    INPUT_FIELD     = (By.CSS_SELECTOR, "#input-example input")
    MESSAGE         = (By.ID, "message")

    def open_page(self):
        self.open(self.URL)

    # --- Чекбокс ---

    def remove_checkbox(self):
        """Кликнуть Remove и дождаться, пока чекбокс удалится из DOM."""
        self.click(self.REMOVE_ADD_BTN)
        # Ждём сообщения "It's gone!" — признак завершения AJAX
        self.wait_text_in_element(self.MESSAGE, "It's gone!", timeout=10)

    def add_checkbox(self):
        """Кликнуть Add и дождаться появления чекбокса."""
        self.click(self.REMOVE_ADD_BTN)
        self.wait_text_in_element(self.MESSAGE, "It's back!", timeout=10)
        self.wait_visible(self.CHECKBOX)

    def is_checkbox_present(self) -> bool:
        """Проверить наличие чекбокса в DOM."""
        return self.is_element_visible(self.CHECKBOX)

    # --- Input field ---

    def enable_input(self):
        """Нажать Enable и дождаться, пока поле станет активным."""
        self.click(self.ENABLE_DISABLE_BTN)
        # Ждём сообщения "enabled"
        self.wait_text_in_element(self.MESSAGE, "enabled", timeout=10)
        # Ждём, пока поле реально станет кликабельным
        self.wait_clickable(self.INPUT_FIELD)

    def disable_input(self):
        """Нажать Disable и дождаться недоступности поля."""
        self.click(self.ENABLE_DISABLE_BTN)
        self.wait_text_in_element(self.MESSAGE, "disabled", timeout=10)

    def is_input_enabled(self) -> bool:
        """Проверить, активно ли поле ввода."""
        return self.wait_present(self.INPUT_FIELD).is_enabled()

    def type_in_input(self, text: str):
        """Ввести текст в поле (только если оно enabled)."""
        self.send_keys(self.INPUT_FIELD, text)

    def get_message(self) -> str:
        return self.get_text(self.MESSAGE)
