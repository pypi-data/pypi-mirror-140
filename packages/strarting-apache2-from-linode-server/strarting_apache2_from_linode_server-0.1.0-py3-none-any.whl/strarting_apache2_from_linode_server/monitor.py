import os
import requests
# import linode_api4
from email.message import EmailMessage
import smtplib
from linode_api4 import LinodeClient,Instance

EMAIL_ADDRESS = 'pratik.corey@gmail.com'
EMAIL_PASSWORD=os.getenv('POETRY_email_pass')
msg=EmailMessage()
msg['Subject']='Alert !! Site Being Down'
msg['from']=EMAIL_ADDRESS
msg['to']='pratik.corey@gmail.com'
msg.set_content('Check your services been down')

def send_email_request():
    with smtplib.SMTP('smtp.gmail.com',587) as smtp: 
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
        smtp.send_message(msg)
    

def restart_server():
    client = LinodeClient(os.getenv('POETRY_LINODE_API'))
    # for instances in client.linode.instances():
    #     print(f'{instances.label}--->{instances.id}')
    instance=client.load(Instance,35049636)
    instance.reboot()


def main():
    try:
        resp=requests.get("http://170.187.252.163",timeout=5)
        if resp.status_code !=200:
            send_email_request()
            restart_server()
    except Exception as e:
        send_email_request()
        restart_server()  
    # print(os.getenv('POETRY_EMAIL_ADDRESS'))
    # print(os.getenv('POETRY_LINODE_API'))
    # print(os.getenv('POETRY_email_pass'))

if __name__ == '__main__':
    main()