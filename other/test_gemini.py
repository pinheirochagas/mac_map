#%%
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#%%
def check_reservations():
    url = "https://www.exploretock.com/lion-dance-cafe-oakland/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # This is a placeholder; you'll need to find the correct element and condition
    reservations_open = soup.find("some_element", class_="some_class")

    if reservations_open:
        print("Reservations at Lion Dance Cafe are now open!")
        send_email()
    return reservations_open

def send_email():
    sender_email = "your_email@example.com"
    receiver_email = "ppinheirochagas@gmail.com"
    password = "your_password"  # Be cautious with storing passwords

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Reservation Available"

    body = "Reservations at Lion Dance Cafe are now open!"
    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

#%%
# You need to set this to run daily using an external scheduler
reservations_open = check_reservations()

# %%
