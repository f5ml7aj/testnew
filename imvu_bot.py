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
        
import requests  # الاستيرادات الأساسية

def get_token_from_api(email, password):
    """إرسال طلب API لتسجيل الدخول واستخراج التوكن."""
    url = "https://api.imvu.com/login"
    payload = {"email": email, "password": password}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")  # تحقق من المفتاح الصحيح للتوكن
            if token:
                print(f"تم استخراج التوكن بنجاح: {token}")
                return token
            else:
                print("التوكن غير موجود في الرد.")
                return None
        else:
            print(f"فشل تسجيل الدخول. كود الحالة: {response.status_code}, الرد: {response.text}")
            return None
    except Exception as e:
        print(f"حدث خطأ أثناء طلب التوكن: {e}")
        return None

# الدالة التالية تعتمد على get_token_from_api
def login(account):
    """تسجيل الدخول باستخدام API أو Selenium."""
    token = get_token_from_api(account["email"], account["password"])  # المحاولة الأولى مع API
    if token:
        print(f"تم تسجيل الدخول باستخدام API. التوكن: {token}")
        return token  # التوكن جاهز للاستخدام
    
    print("لم يتم استخراج التوكن من API. المحاولة باستخدام Selenium...")
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
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn.btn-primary"))
        )
        save_click_location_screenshot(login_button, "login_clicked")
        human_like_delay()
        login_button.click()
        wait_for_page_to_load()

        print(f"تم تسجيل الدخول بنجاح باستخدام Selenium للحساب: {account['email']}")
    except Exception as e:
        print(f"خطأ أثناء تسجيل الدخول باستخدام Selenium للحساب: {e}")



def open_url_from_file(file_path):
    """فتح الرابط الموجود في ملف."""
    try:
        with open(file_path, "r") as file:
            url = file.readline().strip()
            if url:
                driver.get(url)
                wait_for_page_to_load()
                print(f"تم فتح الرابط: {url}")
                
                # أخذ لقطة شاشة بعد فتح الرابط
                screenshot_path = f"screenshots/{screenshot_counter:04d}_post_url_open.png"
                driver.save_screenshot(screenshot_path)
                print(f"تم أخذ لقطة شاشة بعد فتح الرابط وحفظها في: {screenshot_path}")
                
                # الضغط على زر Follow بعد فتح الصفحة
                click_follow_button_multiple_times()
            else:
                print("الرابط غير موجود في الملف.")
    except Exception as e:
        print(f"خطأ أثناء فتح الرابط من الملف: {e}")

def take_screenshot_after_delay():
    """أخذ لقطة شاشة بعد تسجيل الدخول."""
    human_like_delay(15, 15)  # تأخير لمدة 15 ثانية
    screenshot_path = f"screenshots/{screenshot_counter:04d}_post_login.png"
    driver.save_screenshot(screenshot_path)
    print(f"تم أخذ لقطة شاشة بعد 15 ثانية وحفظها في: {screenshot_path}")
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

import requests
def click_follow_button_multiple_times():
    """الضغط على زر المتابعة عدة مرات."""
    try:
        follow_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.follow"))
        )
        for _ in range(3):  # الضغط 3 مرات كمثال
            save_click_location_screenshot(follow_button, "follow_button_clicked")
            follow_button.click()
            human_like_delay(2, 4)
        print("تم الضغط على زر المتابعة بنجاح.")
    except Exception as e:
        print(f"خطأ أثناء الضغط على زر المتابعة: {e}")

def click_follow_button_with_token(token):
    """إرسال طلب متابعة باستخدام التوكن."""
    try:
        # إعداد الهدرز
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        }

        # URL الخاص بزر المتابعة (يجب تحديثه بناءً على الموقع)
        follow_url = "https://api.imvu.com/profile/profile-user-376547310/subscriptions/profile-user-352763477?limit=50"

        # إعداد البيانات
        payload = {"follow": True}

        # إرسال الطلب
        response = requests.post(follow_url, headers=headers, data=payload)
        if response.status_code == 200:
            print("تم إرسال طلب المتابعة بنجاح.")
        else:
            print(f"فشل في إرسال طلب المتابعة: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"حدث خطأ أثناء إرسال طلب المتابعة: {e}")
        
def follow_with_token():
    """استخدام التوكن لتنفيذ المتابعة."""
    token = get_token_from_page()
    if token:
        click_follow_button_with_token(token)
    else:
        print("التوكن غير موجود، لا يمكن متابعة الحساب.")
        

# تحميل الحسابات من الملف
accounts = load_accounts_from_file("accounts.txt")

# تحميل الحسابات من الملف
accounts = load_accounts_from_file("accounts.txt")

# تسجيل الدخول إلى كل حساب
for account in accounts:
    try:
        login(account)  # تسجيل الدخول باستخدام الحساب
        follow_with_token()  # محاولة استخدام التوكن للمتابعة
        
        # فتح الرابط من الملف والضغط على زر Follow
        open_url_from_file("link.txt")
        
        # أخذ لقطة شاشة
        take_screenshot_after_delay()
    except Exception as e:
        print(f"حدث خطأ مع الحساب: {account['email']}, الخطأ: {e}")
driver.quit()
