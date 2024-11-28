import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# إعداد المتصفح
options = Options()
options.add_argument("--headless")  # تشغيل المتصفح في الخلفية
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

# ملف الحسابات
accounts_file = "accounts.txt"

# الحساب الذي سيتم عمل فولو له
target_username = "target_account"

# دالة تسجيل الدخول
def login(email, password):
    try:
        driver.get("https://secure.imvu.com/welcome/login/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        ).send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-submit").click()
        time.sleep(5)
        if "login" in driver.current_url:
            print(f"فشل تسجيل الدخول: {email}")
            return False
        print(f"تم تسجيل الدخول بنجاح: {email}")
        return True
    except Exception as e:
        print(f"حدث خطأ أثناء تسجيل الدخول: {e}")
        return False

# دالة عمل الفولو
def follow_user(username):
    try:
        driver.get(f"https://api.imvu.com/user/{username}/follow")
        time.sleep(3)
        print(f"تم عمل فولو للحساب: {username}")
    except Exception as e:
        print(f"حدث خطأ أثناء عمل فولو: {e}")

# قراءة الحسابات من الملف
def process_accounts():
    try:
        with open(accounts_file, "r") as file:
            accounts = file.readlines()
        for account in accounts:
            email, password = account.strip().split(":")
            if login(email, password):
                follow_user(target_username)
            driver.delete_all_cookies()  # حذف الكوكيز قبل الحساب التالي
    except FileNotFoundError:
        print("ملف الحسابات غير موجود!")
    except Exception as e:
        print(f"حدث خطأ أثناء معالجة الحسابات: {e}")

# تشغيل البوت
if __name__ == "__main__":
    process_accounts()
    driver.quit()
