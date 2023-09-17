import os
import slack_sdk as slack
import config

'''
    How to get a token:
    1. Go to https://api.slack.com/apps/
    2. Click Create New App and follow the wizard
    3. Go to your app and go to ‘OAuth & Permissions’
    4. Under Scopes give the bot the following permissions
        chat:write, chat:write.customize, chat:write.public
'''
slack_oauth = 'XXXYourTokenXXX'
# Number of files script can leave unsorted before it alerts you
alert_threshold = 20
# Channel you want the slack bot to post in.
slack_channel = 'apo'

def count_unsorted():
    count = 0
    for path in os.listdir(config.unsorted_path):
        if os.path.isfile(os.path.join(config.unsorted_path, path)):
            count += 1
    return count
        
def send_alert(file_count):
    client = slack.WebClient(token=slack_oauth)
    client.chat_postMessage(
        channel=slack_channel,
        text=f'{file_count} files need to be manually sorted',
        icon_emoji = ':camera:',
        username = 'apo'
        )  
    
def main():
    file_count = count_unsorted()
    if file_count > alert_threshold:
        send_alert(file_count)

if __name__ == '__main__':
    main()