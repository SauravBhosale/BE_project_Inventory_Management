import smtplib
sender_email= "sauravbhosale55@gmail.com"
sender_password="saurav55"
receiver_email="sauravbhosale55@gmail.com"
message="ITEM ADDED"

server = smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login(sender_email,sender_password)
print('loginsucess')
server.sendmail(sender_email,receiver_email,message)
