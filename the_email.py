import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()
EMAIL_ADDRESS = os.getenv('FIRST_EMAIL')
EMAIL_PASSWORD = os.getenv('SECRET_KEY')


class Email:
    def __init__(self, user, name):
        msg = EmailMessage()
        msg['Subject'] = f'Welcome for signing up, {name}.'
        msg['From'] = EMAIL_PASSWORD
        msg.set_content('''
                    <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Email</title>
                    <!-- Bootstrap Link -->
                    <link crossorigin="anonymous" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
                          integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" rel="stylesheet">
                    <!-- Google fonts -->
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;800&display=swap" rel="stylesheet">

                    <style>
                        body {
                            text-align: center;
                            font-family: 'Open Sans', sans-serif;

                        }   
                    </style>
                </head>
                <body>
                    <div class="container" style="font-weight: 800; text-align: center; margin-top: 30px; padding: 10px; background-color: #ffc26f;"><h1 style="text-align: center; font-weight: 800; font-size: 50px;">Welcome!</h1></div>
                    <div class="container">
                        <p style="text-align: center; padding-top: 30px; font-size: 25px;">Thank you so much for joining the community for London Cafes.</p>
                        <p style="text-align: center; padding-bottom: 30px; font-size: 18px;">If you have any early feedback on features you would like to see or anything else, kindly drop a reply to this email. It would be super helpful😃.</p>

                        <hr style="top: 10px; border: none; height: 10px; background-color: grey;">
                        <p style="text-align: center; margin-top: 25px; font-size: 12px; font-style: italic;">© Copyright 2023 Swifty. All rights reserved.</p>
                        <p style="text-align: center; padding-top: 20px; font-size: 14px;">Want to change how you recieve  these emails?</p>
                        <p style="text-align: center">You can <a href='https://www.google.com/'>update your preferences</a> or <a href='https://www.google.com/'>unsubscribe</a>.</p>
                    </div>

                </body>
                </html>
                ''', subtype='html')
        msg['To'] = user
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

