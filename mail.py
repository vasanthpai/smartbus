import smtplib

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login("ruksar devadi", "shinchan@7865")
server.sendmail(
  "ruksardevadi@address.com", 
  "vasanthpai1996@address.com", 
  "this message is from python")
server.quit()