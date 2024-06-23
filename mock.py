import os

import modal

app = modal.App("example-mockdata")


mock_image = modal.Image.debian_slim(
    python_version="3.10"
).run_commands(  # Doesn't work with 3.11 yet
    "apt-get update",
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "pip install faker",
)

@app.function(image=mock_image)
@modal.web_endpoint()
def details() -> dict:
    from faker import Faker
    import json

    fake = Faker()
    data = {
        "group1": [{
            "name": fake.name(),
            "address": fake.address(),
            "email": fake.email(),
            "phone": fake.phone_number()
        } for _ in range(5)],
        "group2": [{
            "name": fake.name(),
            "address": fake.address(),
            "email": fake.email(),
            "phone": fake.phone_number()
        } for _ in range(5)],

        "logged_at": "245.108.222.0"
    }
        # Convert the data to a JSON string
    data_str = json.dumps(data)
    
    # Return the data as a string within an HTML anchor tag
    return f'<a href="data:application/json,{data_str}">{data_str}</a>'