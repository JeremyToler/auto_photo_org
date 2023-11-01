'''
Auto Photo Org Slack Alert - Jeremy Toler
Sends a message to slack when files cannot be automatically sorted. For 
more info check the readme https://github.com/JeremyToler/auto_photo_org
'''
import slack_sdk as slack
 
def send_alert(file_count, slack_oauth, slack_channel, log):
    try:
        client = slack.WebClient(token=slack_oauth)
        client.chat_postMessage(
            channel=slack_channel,
            text=f'{file_count} files may need to be manually sorted',
            icon_emoji = ':camera:',
            username = 'apo'
            )  
    except:
        log.exception(f'Unknown Slack Error.')