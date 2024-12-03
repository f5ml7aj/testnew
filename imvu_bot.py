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
chrome_options.add_argument("--headless")  # تشغيل المتصفح في وضع خفي
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-logging")

# إعداد خدمة Chrome
service = Service(ChromeDriverManager().install())

# تهيئة متصفح Chrome
driver = webdriver.Chrome(service=service, options=chrome_options)

# إعداد مجلد لحفظ لقطات الشاشة
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

screenshot_counter = 1  # عداد لقطات الشاشة

def save_click_location_screenshot(element, step_name):
    """حفظ لقطة شاشة مع تحديد مكان الضغط."""
    global screenshot_counter
    location = element.location
    size = element.size
    x = int(location["x"] + size["width"] / 2)
    y = int(location["y"] + size["height"] / 2)

    # التقاط لقطة الشاشة
    screenshot_path = f"screenshots/{screenshot_counter:04d}_{step_name}.png"
    driver.save_screenshot(screenshot_path)

    # فتح الصورة ورسم دائرة على مكان الضغط
    image = Image.open(screenshot_path)
    draw = ImageDraw.Draw(image)
    radius = 10
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="red", width=3)
    image.save(screenshot_path)
    screenshot_counter += 1
    print(f"تم حفظ لقطة الشاشة مع تحديد الضغط: {screenshot_path}")

def load_accounts_from_file(file_path):
    """تحميل الحسابات من ملف نصي."""
    accounts = []
    try:
        with open(file_path, "r") as file:
            for line in file.readlines():
                email, password = line.strip().split(":")
                accounts.append({"email": email, "password": password})
        print(f"تم تحميل {len(accounts)} حسابات من الملف.")
    except Exception as e:
        print(f"حدث خطأ أثناء تحميل الحسابات من الملف: {e}")
    return accounts

def skip_cookies_if_present():
    try:
        # البحث عن زر قبول الكوكيز باستخدام الـ Class
        cookie_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn.btn-primary.accept-cookies"))
        )
        save_click_location_screenshot(cookie_button, "cookie_button_found")  # لقطة قبل الضغط
        cookie_button.click()  # الضغط على الزر
        time.sleep(1)  # الانتظار للتأكد من تنفيذ الضغط
        save_click_location_screenshot(driver.find_element(By.TAG_NAME, "body"), "after_cookie_button_click")  # لقطة بعد الضغط
        print("تم الضغط على زر قبول الكوكيز.")
    except Exception as e:
        print(f"خطأ أثناء التعامل مع نافذة الكوكيز: {e}")

def click_sign_in_button():
    try:
        # البحث عن زر "Entrar" والضغط عليه
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.secondary-nav button.sign-in"))
        )
        save_click_location_screenshot(sign_in_button, "sign_in_button_found")  # لقطة قبل الضغط
        sign_in_button.click()  # الضغط على زر "Entrar"
        time.sleep(1)  # الانتظار للتأكد من تنفيذ الضغط
        save_click_location_screenshot(driver.find_element(By.TAG_NAME, "body"), "after_sign_in_button_click")  # لقطة بعد الضغط
        print("تم الضغط على زر 'Entrar'.")
    except Exception as e:
        print(f"خطأ أثناء الضغط على زر 'Entrar': {e}")

def login(account):
    """تسجيل الدخول إلى الموقع باستخدام بيانات الحساب."""
    try:
        # افتح صفحة تسجيل الدخول
        driver.get("https://pt.secure.imvu.com")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # تخطي نافذة الكوكيز إذا ظهرت
        skip_cookies_if_present()

        # الضغط على زر "Entrar"
        click_sign_in_button()

        # التقاط لقطة شاشة لصفحة تسجيل الدخول
        save_click_location_screenshot(driver.find_element(By.TAG_NAME, "body"), "page_loaded")

        # إدخال الإيميل
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "avatarname"))
        )
        email_field.send_keys(account["email"])
        save_click_location_screenshot(email_field, "email_entered")

        # إدخال كلمة المرور
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(account["password"])
        save_click_location_screenshot(password_field, "password_entered")

        # الضغط على زر "تسجيل الدخول"
        login_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn.btn-primary"))
        )
        login_button.click()
        save_click_location_screenshot(login_button, "login_clicked")

        # الانتظار للتأكد من تسجيل الدخول بنجاح
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        save_click_location_screenshot(driver.find_element(By.TAG_NAME, "body"), "after_login")

        print(f"تم تسجيل الدخول بنجاح باستخدام الحساب: {account['email']}")

    except Exception as e:
        print(f"حدث خطأ أثناء تسجيل الدخول: {e}")


def go_to_next_page():
    """الانتقال إلى صفحة معينة بعد تسجيل الدخول."""
    try:
        # الانتقال إلى الصفحة
        driver.get("https://www.imvu.com/next/av/L7AJ/")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # الانتظار لمدة 5 ثواني قبل التقاط لقطة الشاشة
        time.sleep(5)

        # التقاط لقطة شاشة للصفحة بعد الانتقال
        save_click_location_screenshot(driver.find_element(By.TAG_NAME, "body"), "after_waiting_on_page")
        print("تم الانتظار لمدة 5 ثواني وتم التقاط لقطة الشاشة.")

    except Exception as e:
        print(f"حدث خطأ أثناء الانتقال إلى الصفحة: {e}")


# تحميل الحسابات من الملف
accounts = load_accounts_from_file("accounts.txt")

# تسجيل الدخول لكل حساب
for account in accounts:
    login(account)
    go_to_next_page()

# إغلاق المتصفح
driver.quit()
