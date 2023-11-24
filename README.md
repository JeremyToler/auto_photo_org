# Automatic Photo Organizer
<br>
I wanted a way to automatically rename and organize photos that are auto-synced to my NAS. 

### Renaming
Automatically renames photos as follows:<br>
*Year-Month-Day.HourMinuteSecond.City/County.Iter.Ext*

**Some Examples:**<br>
- 2023-07-25.143521.Paris.0000.png<br>
- 2023-07-25.143521.Paris.0001.png<br>
  - The script increments the Iter portion for each file that would have has the same name.<br>
- 2017-10-01.111108.Hawaii_County.0000.png<br> 
  - The script will use the city name if the latitude and longitude GPS metatags line up with a city, otherwise it will use the county name.<br>
- 2004-03-20.143659.0000.jpg<br> 
  - If the script cannot find GPS metadata it simply won't use the city/county data.<br>
- 2006-10-31.0028.jpg<br>
  - If the script cannot find a timestamp it will attempt to parse one out of the file name. This could result in timestamps that do not include the Hour/Min/Sec. As long as the script can determine the Year/Month/Day it will rename the file.<br>
<br>

### Organization
Files are moved into folders based on the year the photo was taken.<br>
Example:
<pre>
.
└── Photos/
    ├── 2023/
    │   ├── 2023-07-25.143521.Paris.0000.png
    │   └── 2023-07-25.150302.Paris.png
    └── 2007/
        ├── 2007-12-24.080149.Mesa.0000.jpg 
        ├── 2007-12-24.080149.Mesa.0001.jpg
        └── 2007-12-24.080150.Mesa.0000.jpg
</pre>
<br>

## How to Use
**Docker CLI** with minimum required variables.

```
docker run -v /path/to/files/to/rename:/data/sorted -v /path/to/renamed/files:/data/unsorted jeremytoler/auto_photo_org:latest
```

**Docker Compose** with all environment variables.

```
version: "3.9"

services:
  auto_photo_org:
    image: jeremytoler/auto_photo_org:latest
    restart: unless-stopped
    environment:
      - USE_SLACK=true #Optional. Default is False.
      - SLACK_OAUTH=${SLACK_OAUTH} #Optional. SlackBot oauth token
      - SLACK_CHANNEL=${SLACK_CHANNEL} #Optional. Slack channel the bot will post to.
      - ALERT_THRESHOLD=25 #Optional. Number of files in the unsorted directory after script runs and before you get pinged. Default is 10.
      - MAX_LOGS=400 #Optional. The number of logs to store, a new log file is created every time the script is run. Default is 100.
      - WAIT_TIME=21600 #Optional. Time in seconds between each time the script is run. Default is 86400 (1 day).
    volumes:
      - /path/to/logs:/data/logs #Optional. This just makes seeing the logs easier. 
      - /path/to/files/to/rename:/data/unsorted
      - /path/to/renamed/files:/data/sorted
```

If you want to get slack notifications you will need to make a slack bot

  1. Go to https://api.slack.com/apps/
  2. Click Create New App and follow the wizard
  3. Go to your app and go to ‘OAuth & Permissions’
  4. Under Scopes give the bot the following permissions
      chat:write, chat:write.customize, chat:write.public

## Troubleshooting
If files are not moved/renamed it could be that script was unable to determine when the photo was taken, or it could be that the script was able to find GPS metadata but was unable to get a response from OpenMaps and did not rename the file so that it could try again the next time the script runs. 

You can check the latest log file to determine why any file was not renamed, or why it was renamed a specific way.  I have only tested this with my own photos and videos.  Feel free to open an issue if you belive that the script is not renaming a file correctly. Please include the log file and the original name of the photo/video so I can find it in the log. 


