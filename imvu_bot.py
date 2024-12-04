from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image, ImageDraw
import os
import time
import random
 
# إعداد متصفح Edge
edge_options = Options()
edge_options.add_argument("--disable-extensions")
edge_options.add_argument("--disable-gpu")
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-logging")
edge_options.add_argument("--start-maximized")  # تشغيل المتصفح بكامل الشاشة
edge_options.add_argument("--headless")  # تشغيل المتصفح بدون واجهة رسومية

# إعداد خدمة Edge
service = Service(EdgeDriverManager().install())

# تهيئة المتصفح
driver = webdriver.Edge(service=service, options=edge_options)

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

def ensure_follow_button_ready():
    try:
        follow_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.people-hash-FAB.Follow .button-wrapper"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", follow_button)
        print("الزر جاهز للاستخدام.")
        return follow_button
    except Exception as e:
        print(f"لم يتم العثور على الزر: {e}")
        return None

def click_follow_button_until_stopped():
    """الضغط على زر Follow بشكل متواصل حتى يتم إيقاف السكربت."""
    try:
        while True:
            wait_for_page_to_load()
            
            # البحث عن زر Follow
            follow_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.people-hash-FAB.Follow .button-wrapper"))
            )

            # حفظ لقطة الشاشة للزر
            save_click_location_screenshot(follow_button, "follow_button_found")

            # تمرير إلى الزر للتأكد من ظهوره
            driver.execute_script("arguments[0].scrollIntoView(true);", follow_button)
            human_like_delay(0.5, 1)  # تأخير بسيط

            # الضغط على الزر
            driver.execute_script("arguments[0].click();", follow_button)
            print("تم الضغط على زر 'Follow'.")
            human_like_delay(1, 2)  # تأخير بين الضغطة والأخرى

            # التحقق من حالة الزر (إذا أصبح "Following")
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.people-hash-FAB.Following .button-wrapper"))
                )
                print("تم تغيير الزر إلى 'Following'.")
            except:
                print("الزر لا يزال 'Follow'، سيتم الضغط مرة أخرى.")
    except KeyboardInterrupt:
        print("تم إيقاف الضغط يدويًا.")
    except Exception as e:
        print(f"حدث خطأ أثناء الضغط المتواصل: {e}")


def click_follow_button_with_delay():
    """البحث عن زر Follow والضغط عليه بعد تأخير."""    
    try:
        # انتظار تحميل الصفحة بالكامل
        wait_for_page_to_load()

        # إضافة تأخير عشوائي قبل الضغط على الزر
        human_like_delay(2, 4)

        # العثور على الزر باستخدام الـ CSS selector المناسب
        follow_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.people-hash-FAB.Follow .button-wrapper"))
        )
        save_click_location_screenshot(follow_button, "follow_button_found")

        # التمرير إلى الزر للتأكد من ظهوره
        driver.execute_script("arguments[0].scrollIntoView(true);", follow_button)
        human_like_delay()

        # الضغط على الزر باستخدام JavaScript إذا لم تعمل الطريقة العادية
        driver.execute_script("arguments[0].click();", follow_button)

        print("تم الضغط على زر 'Follow' بعد تأخير.")

        # إضافة تأخير عشوائي بعد الضغط
        human_like_delay(1, 2)

    except Exception as e:
        print(f"حدث خطأ أثناء الضغط على زر 'Follow': {e}")


# تحميل الحسابات من ملف
accounts = load_accounts_from_file("accounts.txt")

# تسجيل الدخول لجميع الحسابات
for account in accounts:
    login(account)
    time.sleep(2)  # الانتظار بين تسجيل الدخول لكل حساب

# التفاعل مع زر Follow
click_follow_button_with_delay()

# إغلاق المتصفح بعد الانتهاء
driver.quit()
