# example.py

from API.googleform import GoogleForm


# Step 1: Ask for form link
form_url = input("Paste Google Form URL: ")
form = GoogleForm(form_url)

# Step 2: Parse and display detected questions
form.parse_form()

# Step 3: Define Datas (required)
print("\nDefine question purpose using known labels: name, email, phone, feedback, gender, text, etc.")
datas = {}
for idx, q, q_type in form.questions:
    label = input(f"Label for Q{idx} \"{q}\" ({q_type}): ").strip()
    datas[idx] = label
form.set_data_types(datas)

# Step 4: PreFill (optional)
use_prefill = input("Do you want to use prefill values? (y/n): ").lower()
prefill = {}
if use_prefill == 'y':
    for idx, q, q_type in form.questions:
        value = input(f"Prefill for Q{idx} \"{q}\" - use comma-separated list for random choice: ").strip()
        if ',' in value:
            prefill[idx] = [v.strip() for v in value.split(',')]
        elif value:
            prefill[idx] = value
form.set_prefill(prefill)

# Step 5: Submission
mode = input("Submission mode? (random / biased): ").lower()
count = int(input("Number of submissions?: "))
bias_percent = 100 if mode == "biased" else 0
if mode == "biased":
    bias_percent = int(input("Bias % (0-100): "))
form.submit(count=count, mode=mode, bias_percent=bias_percent)
