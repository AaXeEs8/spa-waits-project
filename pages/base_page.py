"""
base_page.py — Базовый класс для всех страниц (Page Object Model).

Ключевая идея темы №4:
  - НЕ используем time.sleep() — он «замораживает» поток на фиксированное время
    независимо от того, загрузился элемент или нет.
  - Используем WebDriverWait + expected_conditions — ожидание прерывается
    сразу как только условие выполнено, и выбрасывает TimeoutException
    если условие не выполнилось за timeout секунд.
"""

import allure
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10   # секунд — стандартное ожидание
AJAX_TIMEOUT   = 15   # секунд — для тяжёлых AJAX-запросов


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        # Основной WebDriverWait — используется во всех методах по умолчанию
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
        # Отдельный wait с увеличенным таймаутом для медленных AJAX
        self.ajax_wait = WebDriverWait(driver, AJAX_TIMEOUT)

    # ------------------------------------------------------------------ #
    #  Навигация                                                            #
    # ------------------------------------------------------------------ #

    def open(self, url: str):
        """Открыть URL и дождаться полной загрузки DOM (document.readyState)."""
        logger.info(f"Открываем URL: {url}")
        self.driver.get(url)
        # Ждём, пока страница полностью загрузится
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete",
            message="Страница не достигла состояния 'complete' за отведённое время"
        )

    # ------------------------------------------------------------------ #
    #  Поиск элементов (Explicit Wait)                                     #
    # ------------------------------------------------------------------ #

    def wait_visible(self, locator, timeout: int = DEFAULT_TIMEOUT):
        """
        Ждём, пока элемент появится В DOM и станет видимым.
        Заменяет: time.sleep(N); driver.find_element(...)
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator),
            message=f"Элемент {locator} не стал видимым за {timeout}с"
        )

    def wait_present(self, locator, timeout: int = DEFAULT_TIMEOUT):
        """
        Ждём присутствия элемента в DOM (не обязательно видимого).
        Используется для скрытых элементов.
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Элемент {locator} не появился в DOM за {timeout}с"
        )

    def wait_clickable(self, locator, timeout: int = DEFAULT_TIMEOUT):
        """Ждём, пока элемент станет кликабельным (visible + enabled)."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator),
            message=f"Элемент {locator} не стал кликабельным за {timeout}с"
        )

    def wait_text_in_element(self, locator, text: str, timeout: int = DEFAULT_TIMEOUT):
        """Ждём появления конкретного текста внутри элемента (AJAX-результат)."""
        return WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element(locator, text),
            message=f"Текст '{text}' не появился в {locator} за {timeout}с"
        )

    def wait_invisible(self, locator, timeout: int = DEFAULT_TIMEOUT):
        """Ждём, пока элемент ИСЧЕЗНЕТ (например, спиннер загрузки)."""
        return WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator),
            message=f"Элемент {locator} не исчез за {timeout}с"
        )

    def wait_count_of_elements(self, locator, count: int, timeout: int = DEFAULT_TIMEOUT):
        """
        Ждём, пока на странице появится ровно N элементов.
        Полезно для таблиц/списков, подгружаемых через AJAX.
        """
        return WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.find_elements(*locator)) >= count,
            message=f"Не появилось {count} элементов {locator} за {timeout}с"
        )

    # ------------------------------------------------------------------ #
    #  Действия                                                             #
    # ------------------------------------------------------------------ #

    def click(self, locator):
        """Кликнуть по элементу после ожидания кликабельности."""
        self.wait_clickable(locator).click()

    def send_keys(self, locator, text: str):
        """Ввести текст в поле после ожидания видимости."""
        el = self.wait_visible(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator) -> str:
        """Получить текст элемента."""
        return self.wait_visible(locator).text

    def is_element_visible(self, locator, timeout: int = 3) -> bool:
        """Проверить видимость элемента без исключения (True/False)."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------ #
    #  Утилиты                                                              #
    # ------------------------------------------------------------------ #

    @allure.step("Сделать скриншот: {name}")
    def take_screenshot(self, name: str):
        """Сохранить скриншот в папку screenshots/."""
        path = f"screenshots/{name}.png"
        self.driver.save_screenshot(path)
        logger.info(f"Скриншот сохранён: {path}")
        # Прикрепляем к Allure-отчёту
        with open(path, "rb") as f:
            allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)

    def get_browser_name(self) -> str:
        """Вернуть имя текущего браузера из capabilities."""
        return self.driver.capabilities.get("browserName", "unknown")

    def execute_js(self, script: str, *args):
        """Выполнить JavaScript."""
        return self.driver.execute_script(script, *args)
