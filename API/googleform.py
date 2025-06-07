import time
import random
import string

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class GoogleForm:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.questions = []  # List of (index, question_text, question_type)
        self.datas = {}      # User-defined labels for each question
        self.prefill = {}    # Optional pre-fill data

    def _start_driver(self):
        chrome_options = Options()
        chrome_options.binary_location = "/snap/bin/chromium"  # or /usr/bin/chromium-browser if you're using apt
        chrome_options.add_argument("--headless=new")  # use new headless mode (for Chromium 109+)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")  # safe
        chrome_options.add_argument("--disable-software-rasterizer")  # extra safe

        chrome_options.binary_location = "/snap/bin/chromium"

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)


    def parse_form(self):
        self._start_driver()
        form_fields = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')

        print("\n[+] Detected Form Questions:\n")
        for idx, field in enumerate(form_fields):
            q_text_elem = field.find_elements(By.CSS_SELECTOR, 'div[role="heading"]')
            q_text = q_text_elem[0].text if q_text_elem else f"Question {idx+1}"

            # Detect type
            if field.find_elements(By.CSS_SELECTOR, 'input[type="text"]'):
                q_type = "text"
            elif field.find_elements(By.CSS_SELECTOR, 'textarea'):
                q_type = "paragraph"
            elif field.find_elements(By.CSS_SELECTOR, 'div[role="radio"]'):
                q_type = "radio"
            elif field.find_elements(By.CSS_SELECTOR, 'div[role="checkbox"]'):
                q_type = "checkbox"
            else:
                q_type = "unknown"

            self.questions.append((idx, q_text, q_type))
            print(f"[{idx}] {q_text} ({q_type})")

        self._stop_driver()

    def set_data_types(self, datas: dict):
        """
        Example:
            {
                0: "name",
                1: "email",
                2: "gender",
                3: "feedback"
            }
        """
        self.datas = datas

    def set_prefill(self, prefill: dict):
        """
        Example:
            {
                0: ["Alice", "Bob"],  # random choice
                1: ["user@example.com"],
                2: ["Male", "Female"],
                3: ["Great", "Okay"]
            }
        """
        self.prefill = prefill

    def _generate_value(self, q_index):
        if q_index in self.prefill:
            val = self.prefill[q_index]
            if isinstance(val, list):
                return random.choice(val)
            return val
        label = self.datas.get(q_index, "text")
        return self._default_for_label(label)



    def _default_for_label(self, label):
        """Generate default values based on known field labels."""
        def random_name():
            first_names = ["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Davis"]
            return f"{random.choice(first_names)} {random.choice(last_names)}"
        def random_email():
            user = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            domains = ["example.com", "mail.com", "test.org", "demo.net"]
            return f"{user}@{random.choice(domains)}"

        def random_phone():
            return "9" + ''.join(random.choices("0123456789", k=9))

        def random_feedback():
            return random.choice([
                "Great work!", "Satisfied.", "Could be better.", "I liked it!", "Please improve."
            ])

        def random_gender():
            return random.choice(["Male", "Female", "Other", "Prefer not to say"])

        defaults = {
            "name": random_name,
            "email": random_email,
            "phone": random_phone,
            "feedback": random_feedback,
            "gender": random_gender,
            "text": lambda: f"Bot_{random.randint(1000,9999)}",
        }

        return defaults.get(label.lower(), defaults["text"])()


    def submit(self, count=1, mode='random', bias_percent=70):
        for i in range(count):
            print(f"\n[+] Submission {i+1}/{count} ({mode})")
            self._start_driver()
            fields = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')

            for idx, field in enumerate(fields):
                q_type = self.questions[idx][2]

                # Handle radio/checkbox
                options = field.find_elements(By.CSS_SELECTOR, 'div[role="radio"], div[role="checkbox"]')
                if options:
                    value = self._generate_value(idx)
                    try:
                        choice_index = int(value)
                        if 0 <= choice_index < len(options):
                            options[choice_index].click()
                        else:
                            random.choice(options).click()
                    except:
                        random.choice(options).click()
                    continue

                # Handle text/paragraph
                inputs = field.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
                for input_box in inputs:
                    value = self._generate_value(idx)
                    input_box.send_keys(str(value))

            # Submit
            try:
                submit_btn = self.driver.find_element(By.XPATH, '//span[contains(text(),"Submit") or contains(text(),"submit")]')
                submit_btn.click()
                print("[✓] Submitted successfully.")
            except:
                print("[!] Submit button not found.")

            time.sleep(1)
            self._stop_driver()
