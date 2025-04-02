import os
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

FB_EMAIL = os.getenv("FB_EMAIL")
FB_PASSWORD = os.getenv("FB_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

SEARCH_TERMS = [
    "Toyota Land Cruiser 1995",
    "Toyota Land Cruiser 1996",
    "Toyota Land Cruiser 1997",
    "Toyota Land Cruiser 1998",
    "Toyota Land Cruiser 1999",
    "Toyota Land Cruiser 2000",
    "Toyota Land Cruiser 2001",
    "Toyota Land Cruiser 2002",
    "Toyota Land Cruiser 2003",
    "Toyota Land Cruiser 2004",
    "Toyota Land Cruiser 2005",
    "Toyota Land Cruiser 2006",
    "Toyota Land Cruiser 2007",
    "Toyota Land Cruiser 2008",
    "Toyota Land Cruiser 2009",
    "Lexus LX 470",
    "Lexus GX 470"
]

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, text)
    server.quit()

def check_marketplace():
    print("Checking Facebook Marketplace...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.facebook.com/login")
        page.fill("input[name='email']", FB_EMAIL)
        page.fill("input[name='pass']", FB_PASSWORD)
        page.click("button[name='login']")
        page.wait_for_timeout(5000)

        for term in SEARCH_TERMS:
            query = term.replace(" ", "%20")
            url = f"https://www.facebook.com/marketplace/100623561313951/search?query={query}"
            page.goto(url)
            page.wait_for_timeout(3000)
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            listings = soup.find_all("a", href=True)
            for listing in listings:
                href = listing['href']
                if '/marketplace/item/' in href:
                    title = listing.get_text()
                    link = f"https://www.facebook.com{href}"
                    send_email(f"New listing: {title}", link)
                    print(f"Found: {title} - {link}")
        browser.close()

schedule.every(10).minutes.do(check_marketplace)

print("Bot started. Watching Facebook Marketplace...")
check_marketplace()
while True:
    schedule.run_pending()
    time.sleep(60)
