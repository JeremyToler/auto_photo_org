# Path to image files that will be renamed and sorted
unsorted_path = 'C:\\Users\\Jeremy\\Pictures\\test\\unsorted'

# Path you want the images saved
sorted_path = 'C:\\Users\\Jeremy\\Pictures\\test'

'''
Nominatum (Open Street Maps) is used to proccess GPS data. 
Put in any name so Nominatum can track useage.
Leaving this blank may get you blocked.
'''
user_agent = ''

# Number of files script can leave unsorted before it alerts you
alert_threshold = 20

# Leave empty if you do not want to use the slack bot
slack_oauth = ''

# Channel you want the slack bot to post in.
slack_channel = 'apo'

# Set to true if you need more debug info.
debug_mode = False