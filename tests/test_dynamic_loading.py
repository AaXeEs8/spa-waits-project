"""
test_dynamic_loading.py — Тема №4: Explicit Waits для SPA.

Что проверяем:
  1. Dynamic Loading Example 1 — элемент СКРЫТ в DOM (display:none),
     после нажатия Start становится видимым.
  2. Dynamic Loading Example 2 — элемент НЕТ в DOM, добавляется
     через AJAX после нажатия Start.
  3. Dynamic Controls — чекбокс и поле ввода добавляются/удаляются
     без перезагрузки страницы.

Ключевой принцип: НЕТ ни одного time.sleep()!
Каждое ожидание — через WebDriverWait + expected_conditions.

Браузеры: Chrome, Firefox, Edge (параметризованы через conftest.py).
"""

import pytest
import allure
import logging

from pages.dynamic_page import DynamicLoadingPage, DynamicControlsPage

logger = logging.getLogger(__name__)


# ======================================================================== #
#  БЛОК 1: Тестирование Dynamic Loading (AJAX-контент)                     #
# ======================================================================== #

@allure.feature("Explicit Waits — AJAX-контент")
class TestDynamicLoading:

    @allure.story("Dynamic Loading: Example 1 (скрытый элемент)")
    @allure.title("Элемент появляется после AJAX-загрузки (пример 1)")
    @allure.description(
        "Нажимаем Start. Элемент был скрыт (display:none). "
        "Explicit Wait ждёт появления текста 'Hello World!' без sleep()."
    )
    def test_dynamic_loading_example1(self, driver):
        """
        Тест проверяет:
        - Лоадер появляется после клика
        - Лоадер исчезает когда AJAX завершён
        - Текст 'Hello World!' виден
        """
        browser = driver.capabilities.get("browserName", "unknown")
        logger.info(f"[{browser}] Запуск теста: Dynamic Loading Example 1")

        page = DynamicLoadingPage(driver)

        with allure.step("Открываем страницу Dynamic Loading — пример 1"):
            page.open_example(1)

        with allure.step("Нажимаем кнопку Start"):
            page.click_start()

        with allure.step("Ожидаем завершения AJAX-загрузки (без sleep!)"):
            page.wait_for_loading_to_finish()

        with allure.step("Проверяем текст результата"):
            result = page.get_result_text()
            logger.info(f"[{browser}] Получен текст: '{result}'")
            assert "Hello World!" in result, (
                f"[{browser}] Ожидался текст 'Hello World!', получено: '{result}'"
            )

        page.take_screenshot(f"dynamic_loading_ex1_{browser}")

    @allure.story("Dynamic Loading: Example 2 (элемент рендерится AJAX-ом)")
    @allure.title("Элемент добавляется в DOM через AJAX (пример 2)")
    @allure.description(
        "В примере 2 элемент изначально ОТСУТСТВУЕТ в DOM — "
        "он создаётся динамически через JavaScript после ответа сервера."
    )
    def test_dynamic_loading_example2(self, driver):
        """
        Принципиальное отличие от примера 1:
        - presence_of_element_located ждёт появления элемента в DOM
        - Не просто видимости (visibility_of_element_located)
        """
        browser = driver.capabilities.get("browserName", "unknown")
        logger.info(f"[{browser}] Запуск теста: Dynamic Loading Example 2")

        page = DynamicLoadingPage(driver)

        with allure.step("Открываем страницу Dynamic Loading — пример 2"):
            page.open_example(2)

        with allure.step("Нажимаем Start"):
            page.click_start()

        with allure.step("Ожидаем исчезновения лоадера"):
            page.wait_for_loading_to_finish()

        with allure.step("Проверяем наличие текста в DOM"):
            result = page.get_result_text()
            logger.info(f"[{browser}] Получен текст: '{result}'")
            assert "Hello World!" in result, (
                f"[{browser}] AJAX не вернул ожидаемый контент: '{result}'"
            )

        page.take_screenshot(f"dynamic_loading_ex2_{browser}")

    @allure.story("Повторный запуск AJAX")
    @allure.title("Загрузка работает при повторном открытии страницы")
    def test_reload_and_wait_again(self, driver):
        """
        Проверяем что после reload страница снова корректно
        отрабатывает AJAX (нет кэшированного состояния).
        """
        browser = driver.capabilities.get("browserName", "unknown")
        page = DynamicLoadingPage(driver)

        with allure.step("Первый запуск"):
            page.open_example(1)
            page.click_start()
            page.wait_for_loading_to_finish()
            assert "Hello World!" in page.get_result_text()

        with allure.step("Перезагружаем страницу (F5)"):
            driver.refresh()

        with allure.step("Второй запуск — проверяем повторную работу"):
            page.click_start()
            page.wait_for_loading_to_finish()
            result = page.get_result_text()
            assert "Hello World!" in result, (
                f"[{browser}] После reload AJAX не отработал: '{result}'"
            )


# ======================================================================== #
#  БЛОК 2: Тестирование Dynamic Controls (добавление/удаление элементов)   #
# ======================================================================== #

@allure.feature("Explicit Waits — Dynamic Controls")
class TestDynamicControls:

    @allure.story("Чекбокс: Remove и Add")
    @allure.title("Чекбокс удаляется и добавляется без перезагрузки")
    @allure.description(
        "Проверяем Remove/Add чекбокса. "
        "После клика ждём AJAX-сообщение, а не фиксированный sleep."
    )
    def test_checkbox_remove_and_add(self, driver):
        browser = driver.capabilities.get("browserName", "unknown")
        logger.info(f"[{browser}] Тест: Remove/Add чекбокса")

        page = DynamicControlsPage(driver)

        with allure.step("Открываем страницу"):
            page.open_page()

        with allure.step("Чекбокс изначально присутствует"):
            assert page.is_checkbox_present(), \
                f"[{browser}] Чекбокс не найден при открытии страницы"

        with allure.step("Удаляем чекбокс (Remove)"):
            page.remove_checkbox()

        with allure.step("Проверяем: чекбокс исчез"):
            assert not page.is_checkbox_present(), \
                f"[{browser}] Чекбокс должен был исчезнуть, но всё ещё виден"
            logger.info(f"[{browser}] Чекбокс успешно удалён")

        with allure.step("Возвращаем чекбокс (Add)"):
            page.add_checkbox()

        with allure.step("Проверяем: чекбокс снова виден"):
            assert page.is_checkbox_present(), \
                f"[{browser}] Чекбокс должен был появиться обратно"

        page.take_screenshot(f"dynamic_controls_checkbox_{browser}")

    @allure.story("Input field: Enable и Disable")
    @allure.title("Поле ввода включается и отключается через AJAX")
    def test_input_enable_disable(self, driver):
        """
        Поле изначально disabled.
        После Enable — ждём кликабельность (не просто видимость!).
        """
        browser = driver.capabilities.get("browserName", "unknown")
        logger.info(f"[{browser}] Тест: Enable/Disable поля ввода")

        page = DynamicControlsPage(driver)

        with allure.step("Открываем страницу"):
            page.open_page()

        with allure.step("Проверяем: поле изначально недоступно"):
            assert not page.is_input_enabled(), \
                f"[{browser}] Поле должно быть disabled по умолчанию"

        with allure.step("Включаем поле (Enable)"):
            page.enable_input()

        with allure.step("Вводим текст в активное поле"):
            test_text = "Selenium Explicit Wait"
            page.type_in_input(test_text)
            logger.info(f"[{browser}] Введён текст: '{test_text}'")

        with allure.step("Отключаем поле (Disable)"):
            page.disable_input()

        with allure.step("Проверяем: поле снова недоступно"):
            assert not page.is_input_enabled(), \
                f"[{browser}] Поле должно быть disabled после нажатия Disable"

        page.take_screenshot(f"dynamic_controls_input_{browser}")

    @allure.story("Сравнение поведения браузеров")
    @allure.title("Время отклика AJAX в разных браузерах")
    def test_ajax_response_timing(self, driver):
        """
        Замеряем фактическое время ожидания AJAX-ответа.
        Это позволяет выявить различия в производительности между браузерами.
        """
        import time
        browser = driver.capabilities.get("browserName", "unknown")

        page = DynamicControlsPage(driver)
        page.open_page()

        start = time.perf_counter()
        page.remove_checkbox()
        elapsed = time.perf_counter() - start

        logger.info(f"[{browser}] Время AJAX Remove: {elapsed:.2f}с")
        allure.attach(
            f"Браузер: {browser}\nВремя Remove AJAX: {elapsed:.3f} сек",
            name="timing_report",
            attachment_type=allure.attachment_type.TEXT
        )

        # Убеждаемся что ответ пришёл быстрее таймаута (15с)
        assert elapsed < 15, \
            f"[{browser}] AJAX занял слишком долго: {elapsed:.2f}с"


# ======================================================================== #
#  БЛОК 3: Параметризованный тест — один тест, разные данные              #
# ======================================================================== #

@allure.feature("Parametrize + Explicit Waits")
class TestParametrized:

    @allure.story("Оба примера Dynamic Loading")
    @pytest.mark.parametrize("example_num, description", [
        (1, "Элемент скрыт display:none"),
        (2, "Элемент добавляется в DOM"),
    ])
    @allure.title("Dynamic Loading Example {example_num}: {description}")
    def test_both_examples(self, driver, example_num, description):
        """
        Параметризованный тест: запускается для примеров 1 и 2,
        в трёх браузерах → итого 6 запусков одного теста.
        """
        browser = driver.capabilities.get("browserName", "unknown")
        logger.info(f"[{browser}] Example {example_num}: {description}")

        page = DynamicLoadingPage(driver)
        page.open_example(example_num)
        page.click_start()
        page.wait_for_loading_to_finish()

        result = page.get_result_text()
        assert "Hello World!" in result, (
            f"[{browser}] Example {example_num} ({description}): "
            f"Текст не совпал: '{result}'"
        )

        page.take_screenshot(f"parametrized_ex{example_num}_{browser}")
