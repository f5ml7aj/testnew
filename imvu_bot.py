import os
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from PIL import Image, ImageDraw
import requests

# إعداد متصفح Firefox
firefox_options = Options()
firefox_options.add_argument("--disable-extensions")
firefox_options.add_argument("--disable-gpu")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--disable-logging")
firefox_options.add_argument("--headless")  # تشغيل المتصفح بدون واجهة رسومية

service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=firefox_options)

def human_like_delay(min_delay=2, max_delay=5):
    time.sleep(random.uniform(min_delay, max_delay))

def load_accounts_from_file(file_path):
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

def load_accounts_to_follow(file_path):
    accounts_to_follow = []
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            accounts_to_follow = data.get("accounts_to_follow", [])
        print(f"تم تحميل {len(accounts_to_follow)} حسابات من الملف.")
    except Exception as e:
        print(f"حدث خطأ أثناء تحميل الحسابات من الملف: {e}")
    return accounts_to_follow

def get_token_from_api(email, password):
    url = "https://api.imvu.com/login"
    payload = {"username": email, "password": password, "gdpr_cookie_acceptance": False}
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "<UA>",
        "X-imvu-application": "welcome/1",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            data = response.json()
            if "denormalized" in data and len(data["denormalized"]) > 0:
                token = data["denormalized"][list(data["denormalized"].keys())[0]]["data"]["sauce"]
                print(f"تم استخراج التوكن بنجاح: {token}")
                return token
            else:
                print("التوكن غير موجود في الرد.")
        else:
            print(f"فشل تسجيل الدخول. كود الحالة: {response.status_code}, الرد: {response.text}")
    except Exception as e:
        print(f"حدث خطأ أثناء طلب التوكن: {e}")
    return None

def login_with_selenium_and_extract_data(account):
    try:
        driver.get("https://pt.secure.imvu.com")
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        # إدخال الإيميل
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "avatarname"))
        )
        email_field.send_keys(account["email"])
        human_like_delay()

        # إدخال كلمة المرور
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(account["password"])
        human_like_delay()

        # الضغط على زر تسجيل الدخول
        login_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.submit"))
        )
        login_button.click()
        human_like_delay()

        # استخراج البيانات المطلوبة
        local_data = {
            "sauce": driver.execute_script('return window.localStorage.getItem("X-imvu-sauce");'),
        }

        # استخراج الكوكيز المطلوبة
        cookies_data = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        required_cookies = ["sid", "window_session", "gid", "osCsid", "sncd"]
        cookies_subset = {k: cookies_data.get(k, None) for k in required_cookies}

        # دمج البيانات
        session_data = {
            "local_data": local_data,
            "cookies": cookies_subset,
        }

        print(f"تم استخراج البيانات: {session_data}")
        return session_data

    except Exception as e:
        print(f"خطأ أثناء تسجيل الدخول واستخراج البيانات باستخدام Selenium: {e}")
        return None

def follow_account_with_session_data(profile_id, session_data):
    url = f"https://api.imvu.com/profile/profile-user-{profile_id}/subscriptions?limit=50"
    
    headers = {
        "Authorization": f"Bearer {session_data['local_data']['sauce']}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": "; ".join([f"{k}={v}" for k, v in session_data['cookies'].items() if v]),
    }

    response = requests.post(url, headers=headers)
    print(f"استجابة API: {response.status_code} - {response.text}")
    if response.status_code == 201:
        print(f"تمت المتابعة بنجاح: {profile_id}")
    else:
        print(f"حدث خطأ أثناء محاولة المتابعة: {response.status_code} - {response.text}")

# تحميل الحسابات
accounts = load_accounts_from_file("accounts.txt")
follow_accounts = load_accounts_to_follow("follow_accounts.json")

# بدء العملية
for account in accounts:
    session_data = login_with_selenium_and_extract_data(account)
    if session_data:
        for follow_account in follow_accounts:
            follow_account_with_session_data(follow_account["profile_id"], session_data)
    else:
        print(f"فشل تسجيل الدخول واستخراج البيانات للحساب: {account['email']}")

driver.quit()
