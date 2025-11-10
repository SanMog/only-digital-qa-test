import pytest
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# URL сайта для тестирования
BASE_URL = "https://only.digital/"

class Locators:
    """
    Класс для хранения всех локаторов, используемых в тесте.
    Централизация локаторов упрощает их поддержку.
    """
    PRELOADER = (By.CSS_SELECTOR, ".Preloader_root__YJpRG")
    COOKIE_BUTTON = (By.XPATH, "//button[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='okay']")
    COOKIE_BANNER_TEXT = (By.XPATH, "//*[contains(text(), 'By continuing to use the website')]")
    FOOTER = (By.TAG_NAME, "footer")
    COPYRIGHT_YEAR = (By.CSS_SELECTOR, ".Footer_year__nyNCc")
    SOCIAL_LINKS = (By.CSS_SELECTOR, "a.SocialButton_root__MjR_H")
    PRIVACY_POLICY_LINK = (By.LINK_TEXT, "Privacy policy")


@pytest.fixture(scope="module")
def driver() -> WebDriver:
    """
    Фикстура для инициализации и закрытия WebDriver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en-US")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_footer_elements_are_present_and_correct(driver: WebDriver):
    """
    Тест проверяет наличие и корректность основных элементов в футере сайта.
    """
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 20)

    # Шаг 1: Ожидание исчезновения прелоадера
    try:
        wait.until(EC.invisibility_of_element_located(Locators.PRELOADER))
    except TimeoutException:
        print("Прелоадер не найден или не исчез, продолжаем выполнение.")

    # Шаг 2: Закрытие плашки Cookie
    try:
        cookie_banner = wait.until(EC.visibility_of_element_located(Locators.COOKIE_BANNER_TEXT))
        driver.execute_script("arguments[0].parentNode.remove();", cookie_banner)
    except TimeoutException:
        print("Плашка Cookie не появилась, пропускаем шаг.")

    # Шаг 3: Прокрутка к футеру и проверка его видимости
    footer_element = wait.until(EC.presence_of_element_located(Locators.FOOTER))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", footer_element)
    wait.until(EC.visibility_of(footer_element))
    assert footer_element.is_displayed(), "Элемент <footer> не отображается после скролла"

    # Шаг 4: Проверка элементов футера
    copyright_element = footer_element.find_element(*Locators.COPYRIGHT_YEAR)
    copyright_html = copyright_element.get_attribute('innerHTML')
    assert "© 2014 - " in copyright_html and "2025" in copyright_html

    social_links = footer_element.find_elements(*Locators.SOCIAL_LINKS)
    assert len(social_links) >= 4, f"Найдено {len(social_links)} ссылок, ожидалось >= 4"
    for link in social_links:
        assert link.get_attribute('href'), f"У ссылки на соцсеть отсутствует href"

    privacy_policy_link = footer_element.find_element(*Locators.PRIVACY_POLICY_LINK)
    assert "pdf" in privacy_policy_link.get_attribute('href'), "Ссылка на политику не ведет на pdf-файл"