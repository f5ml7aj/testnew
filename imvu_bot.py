def login(account):
    """تسجيل الدخول إلى الموقع باستخدام بيانات الحساب."""
    try:
        # افتح صفحة تسجيل الدخول
        driver.get("https://pt.secure.imvu.com")
        wait_for_page_to_load()  # الانتظار حتى يتم تحميل الصفحة بالكامل

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

        # الانتظار حتى يتم تحميل الصفحة بعد تسجيل الدخول (انتظار جاهزية الصفحة)
        wait_for_page_to_load()  # الانتظار حتى يتم تحميل الصفحة بالكامل بعد تسجيل الدخول

        # التقاط لقطة شاشة بعد تحميل الصفحة بالكامل
        save_click_location_screenshot(driver.find_element(By.TAG_NAME, "body"), "after_page_load")

        print(f"تم تسجيل الدخول بنجاح باستخدام الحساب: {account['email']}")

    except Exception as e:
        print(f"حدث خطأ أثناء تسجيل الدخول: {e}")
