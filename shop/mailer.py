import smtplib

gmail_user = 'masterdungen99@gmail.com'
gmail_password = 'ojjpfyhckwzytdmx'

sender = gmail_user
receivers = ['swarajballal2425@gmail.com']#recipient address
subject = 'AI Online Shopping '
body = 'Hi Aziz'

#go ahead adhh the above
def mail(request, items, id):
    message = """From: AI Online Shopping <admin@shop.com>
    To: To Person <swarajballal2425@gmail.com>
    Subject: AI Online Shopping

    Hi {{request.user.customer}},

    Thank you for purchasing below products, please note that you order id is {{id}}

    {{items}}

    Regards,
    AI Online Shopping Team

    """

    try:
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sender, receivers, message)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)
