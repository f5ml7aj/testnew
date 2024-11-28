from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw
import os
import time
from webdriver_manager.firefox import GeckoDriverManager

# إعداد المتصفح
options = Options()
options.add_argument("--headless")  # لتشغيل المتصفح في وضع خفي
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

# إعداد مجلد لحفظ لقطات الشاشة
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

screenshot_counter = 1  # عداد الصور

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

# بيانات تسجيل الدخول
accounts = [
    {"email": "your_email@example.com", "password": "your_password"}  # أضف الحسابات هنا
]

def login(account):
    try:
        # افتح صفحة تسجيل الدخول
        driver.get("https://secure.imvu.com/welcome/login/")  # عدّل الرابط إذا لزم الأمر
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        # التحقق من وجود صفحة الكوكيز والضغط على زر "قبول" إذا كانت موجودة
        try:
            cookie_accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
            )
            cookie_accept_button.click()
            print("تم تخطي صفحة الكوكيز بنجاح")
            save_click_location_screenshot(cookie_accept_button, "cookie_accepted")
        except:
            print("لم يتم العثور على صفحة الكوكيز أو تم تخطيها بالفعل")

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

# تسجيل الدخول لكل حساب
for account in accounts:
    login(account)

# إغلاق المتصفح
driver.quit()
