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
import json

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
import json

# الدالة لتحميل الحسابات التي سيتم متابعتها
def load_accounts_to_follow(file_path):
    """تحميل الحسابات التي سيتم متابعتها من ملف JSON."""
    accounts_to_follow = []
    try:
        with open(file_path, "r") as file:
            data = json.load(file)  # تحميل البيانات من الملف بتنسيق JSON
            accounts_to_follow = data.get("accounts_to_follow", [])  # الحصول على قائمة الحسابات
        print(f"تم تحميل {len(accounts_to_follow)} حسابات من الملف.")
    except Exception as e:
        print(f"حدث خطأ أثناء تحميل الحسابات من الملف: {e}")
    return accounts_to_follow


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

import requests

# باقي الكود
import requests

# دالة get_token_from_api يجب أن تكون هنا قبل استخدامها
def get_tokens_from_api(email, password):
    """إرسال طلب API لتسجيل الدخول واستخراج جميع التوكنات الممكنة."""
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
            tokens = []
            
            # تحقق من أن هناك توكنات متعددة أو معلومات أخرى
            if "id" in data:
                login_id = data["id"]
                print(f"تم استخراج الـ ID بنجاح: {login_id}")
                token = login_id.split("/")[-1]  # استخراج التوكن كجزء من الـ ID
                tokens.append(token)
                print(f"تم استخراج التوكن بنجاح: {token}")
                
                # في حالة وجود توكنات أخرى يمكنك التعامل مع قيم إضافية هنا إذا كان الرد يحتوي عليها
                if "other_tokens" in data:  # مثال توكنات إضافية
                    for token in data["other_tokens"]:
                        tokens.append(token)
                        print(f"تم استخراج توكن إضافي بنجاح: {token}")

                return tokens  # إرجاع قائمة بكل التوكنات المستخرجة
            else:
                print("الـ ID غير موجود في الرد.")
                return None
        else:
            print(f"فشل تسجيل الدخول. كود الحالة: {response.status_code}, الرد: {response.text}")
            return None
    except Exception as e:
        print(f"حدث خطأ أثناء طلب التوكن: {e}")
        return None

# دالة للتأكد من صحة التوكن
def is_token_valid(token):
    """التحقق من صحة التوكن قبل محاولة استخدامه."""
    return token is not None and len(token) > 0

# داخل الدالة login
import requests

# استبدل هذا بمولد User-Agent عشوائي إذا لزم الأمر
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

def login_and_get_token(user, password):
    login_url = "https://api.imvu.com/login"
    payload = {
        "username": user,
        "password": password,
        "gdpr_cookie_acceptance": False
    }
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": UA,
        "Host": "api.imvu.com",
        "Connection": "keep-alive",
        "Content-Length": "93",
        "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
        "Accept": "application/json; charset=utf-8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    response = requests.post(login_url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "status" in data and data["status"] == "success":
            print(f"Login successful for {user}")
            cid = data.get("cid", "")
            sid = response.cookies.get("osCsid")
            sn = response.cookies.get("sncd")
            nm = response.cookies.get("_imvu_avnm")
            sess = response.cookies.get("browser_session")
            sess2 = response.cookies.get("window_session")

            return cid, sid, sn, nm, sess, sess2
        else:
            print(f"Login failed for {user}. Error: {data.get('error', 'Unknown error')}")
    else:
        print(f"Request failed. Status code: {response.status_code}")
    return None, None, None, None, None, None

# قراءة الحسابات من ملف
def read_accounts(file_path):
    accounts = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # افترض أن الحسابات تأتي بالشكل "username:password"
                account = line.strip().split(":")
                if len(account) == 2:
                    accounts.append((account[0], account[1]))
    except FileNotFoundError:
        print(f"File {file_path} not found!")
    return accounts

# تنفيذ تسجيل الدخول وطلب المحفظة
def get_wallet_data():
    accounts = read_accounts("accounts.txt")  # تأكد من تحديث المسار إلى ملف الحسابات
    for user, password in accounts:
        cid, sid, sn, nm, sess, sess2 = login_and_get_token(user, password)
        if cid:
            wallet_url = f"https://api.imvu.com/wallet/wallet-{cid}"
            wallet_response = requests.get(wallet_url, headers={
                "Accept": "application/json; charset=utf-8",
                "Cookie": f"osCsid={sid}; window_session={sess2}; sncd={sn}; _imvu_avnm={nm}",
                "User-Agent": UA
            })
            print(f"Wallet data for {user}: {wallet_response.json()}")

# استدعاء الوظيفة للحصول على بيانات المحفظة
get_wallet_data()


def check_token_validity(token):
    """التحقق من صحة التوكن."""
    url = "https://api.imvu.com/userinfo"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("التوكن صالح!")
        return True
    elif response.status_code == 401:
        print("التوكن غير صالح!")
        return False
    else:
        print(f"فشل في التحقق من التوكن: {response.status_code} - {response.text}")
        return False


def follow_account_with_token(profile_id, token):
    """متابعة الحساب باستخدام التوكن."""
    if not is_token_valid(token):
        print("التوكن غير صالح. لا يمكن المتابعة.")
        return
    
    url = f"https://api.imvu.com/profile/profile-user-{profile_id}/subscriptions?limit=50"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-imvu-application": "next_desktop/1",
        "X-imvu-sauce": "dDCGW-Dcpf1wuW5KIF0acH-v2WU="  # تأكد من صحة هذه القيمة
    }

    response = requests.post(url, headers=headers)

    print(f"استجابة API: {response.status_code} - {response.text}")  # طباعة تفاصيل الاستجابة
    
    if response.status_code == 201:
        print(f"تمت المتابعة بنجاح: {profile_id}")
    elif response.status_code == 204:
        print(f"تمت المتابعة بنجاح ولكن لا يوجد محتوى مرفق: {profile_id}")
    else:
        print(f"حدث خطأ أثناء محاولة المتابعة: {response.status_code} - {response.text}")

# تحميل الحسابات التي سيتم متابعتها من ملف
follow_accounts = load_accounts_to_follow("follow_accounts.json")

# تحميل الحسابات من الملف (المستخدمة لتسجيل الدخول)
accounts = load_accounts_from_file("accounts.txt")

for account in accounts:
    try:
        token = get_token_from_api(account["email"], account["password"])  # استخراج التوكن باستخدام API
        if token:
            print(f"تم تسجيل الدخول باستخدام API. التوكن: {token}")
            for account_to_follow in follow_accounts:
                print(f"متابعة الحساب: {account_to_follow['username']} - Profile ID: {account_to_follow['profile_id']}")
                follow_account_with_token(account_to_follow["profile_id"], token)
        else:
            print(f"لم يتم استخراج التوكن من API. المحاولة باستخدام Selenium...")
            token = login(account)
            if token:
                for account_to_follow in follow_accounts:
                    print(f"متابعة الحساب: {account_to_follow['username']} - Profile ID: {account_to_follow['profile_id']}")
                    follow_account_with_token(account_to_follow["profile_id"], token)
    except Exception as e:
        print(f"حدث خطأ مع الحساب: {account['email']}, الخطأ: {e}")

driver.quit()
