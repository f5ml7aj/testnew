from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image, ImageDraw
import os
import time
import random
import requests

# إعداد متصفح Firefox
firefox_options = Options()
firefox_options.add_argument("--disable-extensions")
firefox_options.add_argument("--disable-gpu")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--disable-logging")
firefox_options.add_argument("--start-maximized")  # تشغيل المتصفح بكامل الشاشة
firefox_options.add_argument("--headless")  # تشغيل المتصفح بدون واجهة رسومية

# إعداد خدمة Firefox
service = Service(GeckoDriverManager().install())

# تهيئة المتصفح
driver = webdriver.Firefox(service=service, options=firefox_options)

# إعداد مجلد لحفظ لقطات الشاشة
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

screenshot_counter = 1  # عداد لقطات الشاشة

def human_like_delay(min_delay=2, max_delay=5):
    """إضافة تأخير عشوائي لمحاكاة التصفح البشري."""
    time.sleep(random.uniform(min_delay, max_delay))

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
        cookie_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.accept-cookies"))
        )
        save_click_location_screenshot(cookie_button, "cookie_button_found")
        human_like_delay()
        cookie_button.click()
        human_like_delay()
        print("تم الضغط على زر قبول الكوكيز.")
    except Exception as e:
        print("لم يتم العثور على زر الكوكيز، أو تم التعامل معه مسبقًا.")

def click_sign_in_button():
    try:
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.secondary-nav button.sign-in"))
        )
        save_click_location_screenshot(sign_in_button, "sign_in_button_found")
        human_like_delay()
        sign_in_button.click()
        human_like_delay()
        print("تم الضغط على زر 'Entrar'.")
    except Exception as e:
        print("لم يتم العثور على زر 'Entrar'.")

def wait_for_page_to_load():
    """انتظار تحميل الصفحة بالكامل باستخدام readyState."""
    try:
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        print("تم تحميل الصفحة بالكامل.")
    except Exception as e:
        print("حدث خطأ أثناء انتظار تحميل الصفحة.")

def get_token_from_page():
    """استخراج التوكن من الصفحة."""
    try:
        # استخراج التوكن من العناصر المخفية أو JavaScript
        token = driver.execute_script("return document.querySelector('input[name=\"csrf_token\"]').value;")
        print(f"تم استخراج التوكن: {token}")
        return token
    except Exception as e:
        print(f"خطأ أثناء استخراج التوكن: {e}")
        return None

def get_token_from_api(email, password):
    """إرسال طلب API لتسجيل الدخول واستخراج الـ ID والتوكن."""
    url = "https://api.imvu.com/login"
    payload = {"username": email, "password": password, "gdpr_cookie_acceptance": False}
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "<UA>",  # ضع الـ User-Agent العشوائي هنا
        "Host": "api.imvu.com",
        "Connection": "keep-alive",
        "Content-Length": "93",
        "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
        "Accept": "application/json; charset=utf-8",
        "sec-ch-ua-mobile": "?0",
        "X-imvu-application": "welcome/1",
        "sec-ch-ua-platform": "\"Windows\"",
        "Origin": "https://pt.secure.imvu.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://pt.secure.imvu.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            data = response.json()
            if "id" in data:
                login_id = data["id"]
                print(f"تم استخراج الـ ID بنجاح: {login_id}")
                # اعتبار الـ id كـ توكن هنا
                token = login_id.split("/")[-1]  # استخراج التوكن كجزء من الـ ID
                print(f"تم استخراج التوكن بنجاح: {token}")
                return token
            else:
                print("الـ ID غير موجود في الرد.")
                return None
        else:
            print(f"فشل تسجيل الدخول. كود الحالة: {response.status_code}, الرد: {response.text}")
            return None
    except Exception as e:
        print(f"حدث خطأ أثناء طلب التوكن: {e}")
        return None


def login(account):
    """تسجيل الدخول باستخدام API أو Selenium."""
    # محاولة استخراج التوكن من API أولاً
    token = get_token_from_api(account["email"], account["password"])  
    if token:
        print(f"تم تسجيل الدخول باستخدام API. التوكن: {token}")
        follow_with_token(token)  # استخدام التوكن لتنفيذ المتابعة مباشرة
        return token  # التوكن جاهز للاستخدام
    
    print("لم يتم استخراج التوكن من API. المحاولة باستخدام Selenium...")

    # إذا لم نحصل على التوكن من الـ API، نتابع مع تسجيل الدخول عبر Selenium
    try:
        driver.get("https://pt.secure.imvu.com")
        wait_for_page_to_load()
        skip_cookies_if_present()
        click_sign_in_button()

        # إدخال الإيميل
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "avatarname"))
        )
        email_field.send_keys(account["email"])
        save_click_location_screenshot(email_field, "email_entered")
        human_like_delay()

        # إدخال كلمة المرور
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(account["password"])
        save_click_location_screenshot(password_field, "password_entered")
        human_like_delay()

        # الضغط على زر تسجيل الدخول
        login_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.submit"))
        )
        save_click_location_screenshot(login_button, "login_button_found")
        login_button.click()
        human_like_delay()

        # استخراج التوكن بعد تسجيل الدخول
        token = get_token_from_page()
        if token:
            print(f"تم استخراج التوكن: {token}")
            follow_with_token(token)  # استخدام التوكن مباشرة
            return token
        else:
            print("لم يتم العثور على التوكن بعد تسجيل الدخول.")
            return None
    except Exception as e:
        print(f"خطأ أثناء تسجيل الدخول عبر Selenium: {e}")
        return None


# دالة المتابعة باستخدام التوكن
def follow_with_token(token):
    """مثال على دالة المتابعة باستخدام التوكن."""
    if token:
        print(f"متابعة الحساب باستخدام التوكن: {token}")
        # هنا يمكنك إضافة الكود لتنفيذ المهام مثل المتابعة باستخدام التوكن
    else:
        print("لم يتم العثور على التوكن.")


# تحميل الحسابات من الملف
accounts = load_accounts_from_file("accounts.txt")

# تسجيل الدخول إلى كل حساب
for account in accounts:
    try:
        token = login(account)  # تسجيل الدخول باستخدام الحساب
        if token:
            follow_with_token(token)  # استخدام التوكن للمتابعة
    except Exception as e:
        print(f"حدث خطأ مع الحساب: {account['email']}, الخطأ: {e}")

driver.quit()
