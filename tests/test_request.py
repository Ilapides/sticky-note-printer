import requests

response = requests.post(
    "http://localhost:5000/print/tasks",
    json={"tasks": ["Buy milk", "Cash check", "Take out trash!"]}
)

print("Status Code:", response.status_code)
print("Response:", response.json())