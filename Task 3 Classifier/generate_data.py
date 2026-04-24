# generate_data.py
# generates synthetic training data — 160 examples per class = 800 total
# evaluation data is manually written in test.json

import json
import random

data = []

billing = [
    "I was charged twice for my subscription this month.",
    "My invoice shows an incorrect amount.",
    "I need a refund for the payment made last week.",
    "Why was I billed for a plan I didn't choose?",
    "My credit card was charged without authorization.",
    "I cancelled my plan but still got charged.",
    "The discount code was not applied to my bill.",
    "I am being charged for features I don't use.",
    "My payment failed but money was deducted.",
    "I need an invoice for my company records.",
    "How do I update my billing information?",
    "I want to switch to annual billing.",
    "My free trial ended and I was charged immediately.",
    "I did not receive a receipt for my last payment.",
    "Can I get a partial refund for unused days?",
    "My bank shows a charge I don't recognize from you.",
    "I was overcharged compared to the plan price.",
    "The payment page shows an error but money was taken.",
    "I need to change my payment method.",
    "Why is my bill higher than last month?",
]

technical_issue = [
    "The app crashes every time I open it.",
    "I cannot log into my account.",
    "The export to CSV button does nothing.",
    "My data is not syncing across devices.",
    "The dashboard is showing incorrect numbers.",
    "I keep getting a 404 error on the settings page.",
    "Notifications are not working on my phone.",
    "The search function returns no results.",
    "I cannot upload files larger than 1MB.",
    "The page takes forever to load.",
    "My account got locked after one wrong password.",
    "The API is returning 500 errors.",
    "Dark mode is not saving my preference.",
    "I cannot delete items from my account.",
    "The mobile app is stuck on the loading screen.",
    "Two factor authentication is not sending codes.",
    "My email integration stopped working.",
    "The report generation feature is broken.",
    "I cannot change my username.",
    "The filter on the list view is not working.",
]

feature_request = [
    "Can you add a dark mode to the app?",
    "It would be great to have CSV export.",
    "Please add support for multiple languages.",
    "I would love a mobile app for Android.",
    "Can you integrate with Slack?",
    "Please add keyboard shortcuts.",
    "It would help to have bulk delete.",
    "Can we get an API for third party integration?",
    "I wish there was a way to schedule reports.",
    "Please add two factor authentication.",
    "Can you add a calendar view?",
    "It would be useful to tag items.",
    "Please support Google login.",
    "Can we have custom email templates?",
    "I would like to export data as PDF.",
    "Please add team collaboration features.",
    "Can you add a search filter by date?",
    "It would be great to have webhook support.",
    "Please allow custom branding.",
    "Can we get usage analytics in the dashboard?",
]

complaint = [
    "Your customer support is terrible.",
    "I have been waiting for a response for three days.",
    "This product is not worth the price.",
    "I am extremely frustrated with the service.",
    "Nobody is responding to my emails.",
    "The product keeps breaking and nobody helps.",
    "I feel ignored by your support team.",
    "This is the worst software I have ever used.",
    "Your team promised a fix two weeks ago and nothing happened.",
    "I am considering leaving because of poor service.",
    "The quality has gone down significantly.",
    "I am very disappointed with recent changes.",
    "Your support team is rude and unhelpful.",
    "I have reported this issue five times with no resolution.",
    "This is unacceptable for a paid product.",
    "I want to escalate this to a manager.",
    "The product does not work as advertised.",
    "I am filing a complaint about your service.",
    "Your response time is completely unacceptable.",
    "I regret signing up for this service.",
]

other = [
    "How do I change my profile picture?",
    "What are your business hours?",
    "Do you have a desktop app?",
    "How do I invite a team member?",
    "Where can I find the documentation?",
    "What payment methods do you accept?",
    "How do I cancel my account?",
    "Is there a student discount available?",
    "How do I change my password?",
    "What is your data retention policy?",
    "Do you offer a free plan?",
    "How do I contact sales?",
    "Where are your servers located?",
    "How do I export my data?",
    "What browsers do you support?",
    "Is there an affiliate program?",
    "How do I enable notifications?",
    "What is the maximum file size I can upload?",
    "How do I add a custom domain?",
    "Where can I find release notes?",
]

templates = {
    "billing": billing,
    "technical_issue": technical_issue,
    "feature_request": feature_request,
    "complaint": complaint,
    "other": other,
}

for label, examples in templates.items():
    for i in range(160):
        base = examples[i % len(examples)]
        # slight variation to avoid exact duplicates
        variations = [
            base,
            base + " Please help.",
            base + " This is urgent.",
            "Hi, " + base.lower(),
            base + " Thank you.",
            base + " I need this resolved soon.",
            base + " Can someone assist?",
            "Hello, " + base.lower(),
        ]
        text = variations[i % len(variations)]
        data.append({"text": text, "label": label})

random.shuffle(data)

with open("data/train.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Generated {len(data)} training examples")