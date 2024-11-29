from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw
import os
import time
from webdriver_manager.chrome import ChromeDriverManager

# إعداد متصفح Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# إعداد خدمة Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# إعداد مجلد لحفظ لقطات الشاشة
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

screenshot_counter = 1

def save_click_location_screenshot(element, step_name):
    """حفظ لقطة شاشة مع تحديد مكان الضغط."""
    global screenshot_counter
    location = element.location
    size = element.size
    x = int(location["x"] + size["width"] / 2)
    y = int(location["y"] + size["height"] / 2)

    screenshot_path = f"screenshots/{screenshot_counter:04d}_{step_name}.png"
    driver.save_screenshot(screenshot_path)

    image = Image.open(screenshot_path)
    draw = ImageDraw.Draw(image)
    radius = 10
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="red", width=3)
    image.save(screenshot_path)
    screenshot_counter += 1
    print(f"تم حفظ لقطة الشاشة: {screenshot_path}")

def skip_cookies_if_present():
    try:
        # الانتظار حتى ظهور نافذة الكوكيز
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'ACEITAR TODOS OS COOKIES')]"))
        )
        cookie_button = driver.find_element(By.XPATH, "//button[contains(text(), 'ACEITAR TODOS OS COOKIES')]")
        save_click_location_screenshot(cookie_button, "cookie_button_found")
        cookie_button.click()
        print("تم الضغط على زر قبول الكوكيز.")
    except Exception as e:
        print("لم يتم العثور على نافذة الكوكيز أو تم تخطيها بالفعل.")

def login(account):
    try:
        # افتح صفحة تسجيل الدخول
        driver.get("https://pt.secure.imvu.com/welcome/login/")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        # تخطي نافذة الكوكيز إذا ظهرت
        skip_cookies_if_present()

        # إدخال بيانات تسجيل الدخول
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "avatarname"))
        )
        email_field.send_keys(account["email"])
        save_click_location_screenshot(email_field, "email_entered")

        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(account["password"])
        save_click_location_screenshot(password_field, "password_entered")

        login_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn.btn-primary"))
        )
        save_click_location_screenshot(login_button, "login_button_found")
        login_button.click()

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        save_click_location_screenshot(driver.find_element(By.TAG_NAME, "body"), "after_login")
        print(f"تم تسجيل الدخول بنجاح باستخدام الحساب: {account['email']}")
    except Exception as e:
        print(f"حدث خطأ أثناء تسجيل الدخول: {e}")

# بيانات تسجيل الدخول
accounts = [
    {"email": "your_email@example.com", "password": "your_password"}
]

# تسجيل الدخول لكل حساب
for account in accounts:
    login(account)

# إغلاق المتصفح
driver.quit()
