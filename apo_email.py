'''
Auto Photo Org Slack Alert - Jeremy Toler
Sends an email when files cannot be automatically sorted. For more info 
check the readme https://github.com/JeremyToler/auto_photo_org
'''
import smtplib

def send_alert(file_count, address, log):
    email = smtplib.SMTP('localhost')
    subject = f'APO Alert {file_count}'
    content = f'''{file_count} files may need to be manually sorted.'''
    message = f"""
        Subject: {subject}
        To: {address}
        From: {address}
        {content}"""
    try:
        result = email.sendmail(address, address, message)
        log.debug(f'smtplib sendmail result: \n {result}')
    except:
        log.exception(f'Unknown e-mail error.')
    email.quit()
