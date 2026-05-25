# SPA Waits Project 🚀

> **Практика: Explicit Waits в Selenium для тестирования SPA с AJAX**

Проект демонстрирует правильное использование **явных ожиданий (Explicit Waits)** вместо `time.sleep()` при автоматизированном тестировании приложений с динамической загрузкой контента через AJAX.

---

## 📋 Описание

Этот проект содержит набор тестов для [The Internet](https://the-internet.herokuapp.com) — специально созданного сайта для обучения Selenium. Фокус на **ожидании элементов**, которые появляются или исчезают без перезагрузки страницы.

### Почему Explicit Waits важны?

❌ **Без ожиданий:**
```python
time.sleep(5)  # Жмём 5 секунд всегда, даже если элемент появился за 0.5с
driver.find_element(...)
```

✅ **С Explicit Waits:**
```python
WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "result")),
    message="Результат не появился"
)  # Ждём максимум 10 сек, но вернёмся ТУТ ЖЕ как только элемент видимый
```

---

## 🎯 Что тестируется

### 1️⃣ **Dynamic Loading — Example 1**
- **Сценарий:** элемент скрыт в DOM (`display:none`)
- **Действие:** нажимаем Start
- **Ожидание:** элемент становится видимым после AJAX-ответа
- **Проверка:** текст "Hello World!" появился на странице

### 2️⃣ **Dynamic Loading — Example 2**
- **Сценарий:** элемента вообще нет в DOM
- **Действие:** нажимаем Start
- **Ожидание:** элемент добавляется в DOM через JavaScript
- **Проверка:** текст "Hello World!" присутствует в DOM

### 3️⃣ **Dynamic Controls — Checkbox**
- **Сценарий:** чекбокс добавляется/удаляется из DOM
- **Действие:** нажимаем Remove → видим сообщение "It's gone!" → нажимаем Add
- **Ожидание:** ждём AJAX-сообщения, а не фиксированное время
- **Проверка:** чекбокс исчезает и появляется

### 4️⃣ **Dynamic Controls — Input Field**
- **Сценарий:** текстовое поле включается/отключается
- **Действие:** нажимаем Enable → вводим текст → нажимаем Disable
- **Ожидание:** ждём, пока поле станет кликабельным
- **Проверка:** поле активно только после Enable

---

## 🛠️ Стек технологий

| Компонент | Версия | Назначение |
|-----------|--------|----------|
| **Selenium** | 4.18.1 | WebDriver для управления браузером |
| **WebDriver Manager** | 4.0.1 | Автоматическая загрузка драйверов браузеров |
| **pytest** | 8.0.0 | Фреймворк для написания тестов |
| **Allure** | 2.13.2 | Красивые отчёты о результатах тестирования |
| **Pillow** | 10.2.0 | Обработка скриншотов |
| **requests** | 2.31.0 | HTTP-запросы |

---

## 📦 Установка

### Требования
- Python 3.8+
- pip или pipenv

### Шаги

1. **Клонируйте репозиторий:**
   ```bash
   git clone <url-репозитория>
   cd spa_waits_project
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate     # Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Запуск тестов

### Запустить все тесты
```bash
pytest
```

### Запустить конкретный тест
```bash
pytest tests/test_dynamic_loading.py::TestDynamicLoading::test_dynamic_loading_example1
```

### Запустить с определённым браузером
Тесты параметризованы (запускаются в Chrome, Firefox, Edge):
```bash
pytest -v
```

### Запустить с логированием
```bash
pytest -v --log-cli-level=DEBUG
```

### Сгенерировать Allure-отчёт
```bash
pytest
allure serve allure-results
```

---

## 📁 Структура проекта

```
spa_waits_project/
├── __main__.py              # Точка входа (если нужен интерактивный режим)
├── requirements.txt         # Зависимости проекта
├── pytest.ini              # Конфигурация pytest
│
├── pages/
│   ├── __init__.py
│   ├── base_page.py         # Базовый класс со всеми Explicit Waits методами
│   └── dynamic_page.py      # Page Object для тестируемых страниц
│
├── tests/
│   ├── __init__.py
│   └── test_dynamic_loading.py  # Основные тесты
│
├── screenshots/             # Папка для скриншотов (создаётся автоматически)
├── allure-results/          # Результаты Allure-отчётов
└── README.md               # Этот файл
```

---

## 🔑 Ключевые концепции

### WebDriverWait + Expected Conditions

Основной паттерн проекта:

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ожидание видимости элемента
wait = WebDriverWait(driver, timeout=10)
element = wait.until(
    EC.visibility_of_element_located((By.ID, "result")),
    message="Элемент не появился за 10 секунд"
)
```

### Page Object Model (POM)

Все локаторы и методы организованы в классах:

```python
class DynamicLoadingPage(BasePage):
    START_BUTTON = (By.CSS_SELECTOR, "#start button")
    FINISH_TEXT = (By.CSS_SELECTOR, "#finish h4")
    
    def click_start(self):
        self.click(self.START_BUTTON)
    
    def get_result_text(self):
        return self.get_text(self.FINISH_TEXT)
```

**Преимущества:**
- ✅ Централизованное управление локаторами
- ✅ Простота обновления (изменили один локатор — работает везде)
- ✅ Читаемость тестов

### Timeouts

| Тип | Значение | Применение |
|-----|----------|----------|
| `DEFAULT_TIMEOUT` | 10 сек | Стандартное ожидание элементов |
| `AJAX_TIMEOUT` | 15 сек | Долгие AJAX-запросы |
| Пользовательский | N сек | Можно передать свой timeout в методы |

---

## 📝 Примеры использования

### Пример 1: Ожидание видимости элемента
```python
def wait_visible(self, locator, timeout=10):
    """Элемент должен быть и в DOM, и видимым."""
    return WebDriverWait(self.driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )
```

### Пример 2: Ожидание исчезновения (спиннер загрузки)
```python
def wait_invisible(self, locator, timeout=10):
    """Используется для индикаторов загрузки."""
    return WebDriverWait(self.driver, timeout).until(
        EC.invisibility_of_element_located(locator)
    )
```

### Пример 3: Ожидание текста в элементе (AJAX-результат)
```python
def wait_text_in_element(self, locator, text, timeout=10):
    """Ждём появления конкретного текста."""
    return WebDriverWait(self.driver, timeout).until(
        EC.text_to_be_present_in_element(locator, text)
    )
```

---

## 🧪 Параметризованные тесты

Одинаковый тест запускается для разных примеров и браузеров:

```python
@pytest.mark.parametrize("example_num, description", [
    (1, "Элемент скрыт display:none"),
    (2, "Элемент добавляется в DOM"),
])
def test_both_examples(self, driver, example_num, description):
    # Один тест × 2 примера × 3 браузера = 6 запусков
    pass
```

---

## 📊 Allure-отчёты

После запуска тестов с Allure будут созданы:
- 📌 **Features** — основные функции (Explicit Waits для AJAX, Dynamic Controls)
- 📖 **Stories** — истории (какие сценарии тестируются)
- 🎯 **Steps** — детализированные шаги каждого теста
- 🖼️ **Attachments** — скриншоты и дополнительные данные

Команда для просмотра:
```bash
allure serve allure-results
```

---

## 🐛 Типичные ошибки и решения

### ❌ Ошибка: `NoSuchElementException`
```python
# Неправильно:
driver.find_element(By.ID, "result").text  # Может не существовать ещё!

# Правильно:
wait.until(EC.presence_of_element_located((By.ID, "result"))).text
```

### ❌ Ошибка: `TimeoutException`
- Элемент не появляется за отведённое время
- **Решение:** увеличьте timeout или проверьте локатор

### ❌ Ошибка: Тест нестабилен
```python
# Неправильно:
time.sleep(5)  # Иногда 5 секунд мало, иногда 5 чересчур много

# Правильно:
wait.until(EC.visibility_of_element_located(locator))
```

---

## 📚 Дополнительные ресурсы

- 📖 [Selenium Documentation — Waits](https://www.selenium.dev/documentation/webdriver/waits/)
- 🌐 [The Internet — практический сайт для тестирования](https://the-internet.herokuapp.com)
- 🎨 [Allure Framework](https://docs.qameta.io/allure/)
- 🧪 [pytest Documentation](https://docs.pytest.org/)

---

## 💡 Советы для обучения

1. **Начните с Example 1** — самый простой сценарий
2. **Экспериментируйте с timeouts** — попробуйте установить меньше/больше
3. **Смотрите Allure-отчёты** — виден полный ход выполнения каждого теста
4. **Добавьте свои тесты** — измените локаторы, добавьте новые проверки
5. **Запускайте в разных браузерах** — убедитесь в кроссбраузерности

---

## 🤝 Участие

Если вы нашли баг или хотите добавить новый тест:
1. Создайте Issue с описанием
2. Сделайте Fork проекта
3. Создайте Pull Request с вашими изменениями

---

## 📄 Лицензия

MIT — используйте этот проект свободно в образовательных целях.

---

## 👨‍💻 Автор

Проект создан как часть **практики волков** 🐺 для обучения Selenium.

---

**Удачи в обучении автоматизированному тестированию! 🎉**

*Помните: `WebDriverWait` — ваш лучший друг. `time.sleep()` — враг стабильности тестов.*