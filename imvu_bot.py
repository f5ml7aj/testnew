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

def extract_follow_button_details():
    """جمع كافة المعلومات المتعلقة بأزرار 'Follow'."""
    follow_buttons_data = {"selenium_info": []}
    try:
        # العثور على جميع أزرار Follow
        follow_buttons = driver.find_elements(By.CSS_SELECTOR, "div.people-hash-FAB.Follow .button-wrapper")
        print(f"تم العثور على {len(follow_buttons)} أزرار 'Follow'.")

        for button in follow_buttons:
            try:
                # جمع التفاصيل
                details = {
                    "text": button.text,
                    "location": button.location,
                    "size": button.size,
                    "html": button.get_attribute("outerHTML")
                }
                follow_buttons_data["selenium_info"].append(details)
                print(f"تم استخراج معلومات الزر: {details}")
            except Exception as e:
                print(f"خطأ أثناء استخراج معلومات الزر: {e}")
        
        # حفظ البيانات في ملف JSON
        with open("follow_buttons_data.json", "w", encoding="utf-8") as file:
            json.dump(follow_buttons_data, file, ensure_ascii=False, indent=4)
        print("تم حفظ معلومات أزرار 'Follow' في ملف 'follow_buttons_data.json'.")
    except Exception as e:
        print(f"فشل استخراج معلومات أزرار 'Follow': {e}")
    return follow_buttons_data

def click_follow_button_multiple_times(retries=5):
    """الضغط على زر الفولو عدة مرات وضمان تسجيل البيانات."""
    for attempt in range(retries):
        try:
            print(f"محاولة رقم {attempt + 1} للضغط على زر 'Follow'.")
            
            # استخراج معلومات الزر
            follow_buttons_data = extract_follow_button_details()
            print(f"تفاصيل الأزرار المستخرجة: {follow_buttons_data}")
            
            click_follow_button()
            break  # إذا نجحت العملية، لا داعي لإعادة المحاولة
        except Exception as e:
            print(f"محاولة الضغط على زر 'Follow' فشلت: {e}. إعادة المحاولة...")
            human_like_delay(2, 3)  # انتظار بين المحاولات


def move_mouse_to_element(element):
    """محاكاة حركة الماوس بشكل تدريجي للوصول إلى العنصر."""
    try:
        # الحصول على موقع العنصر
        location = element.location
        size = element.size
        
        # حساب موقع منتصف العنصر
        x = location['x'] + size['width'] / 2
        y = location['y'] + size['height'] / 2
        
        # محاكاة حركة الماوس باستخدام ActionChains
        actions = ActionChains(driver)
        actions.move_by_offset(1, 1)  # بدء الحركة
        actions.move_to_element_with_offset(element, 0, 0)  # الحركة التدريجية
        actions.perform()
        
        print(f"تمت محاكاة حركة الماوس إلى العنصر عند الموقع ({x}, {y}).")
    except Exception as e:
        print(f"خطأ أثناء تحريك الماوس: {e}")

def save_click_location_screenshot(element, step_name):
    """حفظ لقطة شاشة مع تحديد مكان الضغط، مع تحريك الماوس أولاً."""
    move_mouse_to_element(element)  # تحريك الماوس إلى العنصر
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
        
        driver.get("https://www.imvu.com/next/av/L7AJ/")  # صفحة أخرى بعد الفشل
        wait_for_page_to_load()
        print("تم التوجه إلى الصفحة الجديدة.")



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

def click_follow_button():
    try:
        # البحث عن زر "Follow" والتأكد من أنه قابل للنقر
        follow_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.people-hash-FAB.Follow .button-wrapper"))
        )
        
        # التمرير إلى الزر
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", follow_button)
        print("تم العثور على زر 'Follow'.")

        # التأكد من أن الزر مرئي قبل النقر
        if not follow_button.is_displayed():
            print("زر 'Follow' غير مرئي.")
            return

        # التأكد من أن الزر ليس محجوبًا
        if not follow_button.is_enabled():
            print("زر 'Follow' غير مفعل.")
            return

        # النقر على الزر
        follow_button.click()
        print("تم الضغط على زر 'Follow'.")

        # التحقق من نجاح العملية
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.people-hash-FAB.Following .button-wrapper"))
        )
        print("تم تغيير الزر إلى 'Following'.")

    except Exception as e:
        print(f"فشل الضغط على زر 'Follow': {e}")


def verify_follow_status():
    """التحقق من أن زر Follow قد تم تفعيله."""
    try:
        following_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.people-hash-FAB.Following .button-wrapper"))
        )
        if following_button:
            print("تم التأكد من أن الحساب تم متابعته بنجاح.")
        else:
            print("لم يتم تفعيل المتابعة. قد يكون هناك مشكلة في العملية.")
    except Exception as e:
        print(f"فشل في التحقق من حالة المتابعة: {e}")

# تحميل الحسابات من الملف
accounts = load_accounts_from_file("accounts.txt")

# تسجيل الدخول إلى كل حساب
for account in accounts:
    login(account)

# فتح الرابط من الملف والضغط على زر Follow عدة مرات
open_url_from_file("link.txt")
click_follow_button()
verify_follow_status()

# أخذ لقطة شاشة بعد تأخير
take_screenshot_after_delay()

# إغلاق المتصفح
driver.quit()
