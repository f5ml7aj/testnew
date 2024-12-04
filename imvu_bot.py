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
    """تخطي نافذة الكوكيز إذا كانت موجودة."""
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
    """الضغط على زر تسجيل الدخول."""
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

def switch_to_popup_window():
    """التبديل إلى نافذة منبثقة إذا كانت موجودة."""
    try:
        main_window = driver.current_window_handle
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

        # التبديل إلى النافذة المنبثقة
        for window_handle in driver.window_handles:
            if window_handle != main_window:
                driver.switch_to.window(window_handle)
                print(f"تم التبديل إلى النافذة المنبثقة: {window_handle}")
                break
    except Exception as e:
        print(f"خطأ أثناء التبديل إلى النافذة المنبثقة: {e}")

def switch_back_to_main_window():
    """الرجوع إلى النافذة الأصلية بعد التعامل مع النافذة المنبثقة."""
    try:
        driver.switch_to.window(driver.window_handles[0])
        print("تم الرجوع إلى النافذة الرئيسية.")
    except Exception as e:
        print(f"خطأ أثناء الرجوع إلى النافذة الرئيسية: {e}")

def login(account):
    """تسجيل الدخول إلى الموقع باستخدام بيانات الحساب."""
    try:
        driver.get("https://pt.secure.imvu.com")
        wait_for_page_to_load()

        # تخطي نافذة الكوكيز
        skip_cookies_if_present()

        # الضغط على زر تسجيل الدخول
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

        print(f"تم تسجيل الدخول بنجاح باستخدام الحساب: {account['email']}")
    except Exception as e:
        print(f"خطأ أثناء تسجيل الدخول باستخدام الحساب: {e}")

def click_follow_button_with_delay():
    """البحث عن زر Follow والضغط عليه بعد تأخير."""
    try:
        # انتظار تحميل الصفحة بالكامل
        wait_for_page_to_load()

        # إضافة تأخير عشوائي قبل الضغط على الزر
        human_like_delay(2, 4)

        # العثور على الزر باستخدام XPath
        follow_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='people-hash-FAB Follow']//div[@class='button-wrapper']//div[@class='label label-m' and text()='Follow']"))
        )
        print("تم العثور على زر Follow، الآن سيتم الضغط عليه.")
        save_click_location_screenshot(follow_button, "follow_button_found")

        # استخدام ActionChains لتنفيذ الضغط على الزر
        action = ActionChains(driver)
        action.move_to_element(follow_button).click().perform()

        # إضافة تأخير بعد الضغط للتحقق من النتيجة
        human_like_delay(2, 4)

        print("تم الضغط على زر 'Follow' بعد تأخير.")
        
        # الانتظار لتغيير الزر إلى "Following"
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@class='people-hash-FAB Follow']//div[@class='label label-m']"), "Following"
            )
        )
        print("تم تغيير الزر إلى 'Following' بنجاح.")

        # أخذ لقطة شاشة بعد الضغط على الزر وتغيير النص
        screenshot_path = f"screenshots/{screenshot_counter:04d}_post_following_button.png"
        driver.save_screenshot(screenshot_path)
        print(f"تم أخذ لقطة شاشة بعد تغيير الزر وحفظها في: {screenshot_path}")

    except Exception as e:
        print(f"حدث خطأ أثناء الضغط على زر 'Follow': {e}")
        # محاولة أخذ لقطة شاشة لتشخيص المشكلة
        screenshot_path = f"screenshots/{screenshot_counter:04d}_error_follow_button.png"
        driver.save_screenshot(screenshot_path)
        print(f"تم أخذ لقطة شاشة لتشخيص الخطأ وحفظها في: {screenshot_path}")


def take_screenshot_and_save(step_name):
    """أخذ لقطة شاشة وحفظها مع اسم الخطوة."""
    global screenshot_counter
    screenshot_path = f"screenshots/{screenshot_counter:04d}_{step_name}.png"
    driver.save_screenshot(screenshot_path)
    print(f"تم حفظ لقطة الشاشة: {screenshot_path}")
    screenshot_counter += 1

def main():
    """الخطوات الرئيسية لتنفيذ عملية تسجيل الدخول والتفاعل مع الموقع."""
    accounts = load_accounts_from_file("accounts.txt")
    if accounts:
        for account in accounts:
            login(account)
            open_url_from_file("url.txt")
    else:
        print("لا توجد حسابات للاستخدام.")

# تشغيل البرنامج
main()

# إغلاق المتصفح بعد الانتهاء
driver.quit()
