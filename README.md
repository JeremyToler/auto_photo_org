# Automatic Photo Organizer
<br>
I wanted a way to automatically rename and organize photos that are auto-synced to my NAS. This follows the naming scheme I personally use but now I can run this with a cronjob once a day instead of using a bulk rename program. 

### Renaming
Automatically renames photos as follows:<br>
*Year-Month-Day.HourMinuteSecond.City/County.(Iter).Ext*

**Some Examples:**<br>
- 2023-07-25.143521.Paris.png<br>
  - The script will rename files with as much information as possible.<br>
- 2023-07-25.143521.Paris(1).png<br>
  - If more than one file would have the same name, a number will be added to the end of the file name in parenthesis. <br>
- 2017-10-01.111108.Hawaii_County.png<br> 
  - The script will use the city name if the latitude and longitude GPS metatags line up with a city, otherwise it will use the county name. <br>
- 2004-03-20.143659.jpg<br> 
  - If the script cannot find GPS metadata it simply won't use the city/county data. <br>
- 2006-10-31(8).jpg<br>
  - If the script cannot find a timestamp it will attempt to parse one out of the file name. This could result in timestamps that do not include the Hour/Min/Sec. As long as the script can determine the Year/Month/Day it will rename the file. <br>
<br>

### Organization
Files are moved into folders based on the year the photo was taken.<br>
Example:
<pre>
.
└── Photos/
    ├── 2023/
    │   ├── 2023-07-25.143521.Paris.png
    │   └── 2023-07-25.150302.Paris.png
    └── 2007/
        ├── 2007-12-24.080149.Mesa.jpg 
        ├── 2007-12-24.080149.Mesa(1).jpg
        └── 2007-12-24.080150.Mesa.jpg
</pre>
<br>

## How to Use
**Edit `config.py`**<br><br>
**unsorted_path:** Path to files you want to rename/organize<br>
**sorted_path:** Folder you want the files to move to<br>
**user_agent:** Normally this would be where an API key goes, however OpenMaps simply needs any string to monitor traffic demands.  Any string input works, just don't leave it blank.<br>
_If using a SlackBot to alert when files need manual intervention:_<br>
**alert_threshold:** Number of files in the unsorted directory after script runs and before you get pinged<br>
**slack_oath:** SlackBot oauth token<br>
**slack_channel:** Slack channel the bot will post to<br>
**debug_mode:** Change to true if you need more info from the debug log.  [Further documentation](https://geopy.readthedocs.io/en/stable/index.html?highlight=user_agent)<br>
<br><br>
SlackBot permissions needed:<br>
- chat:write
- chat:write.customize
- chat:write.public
<br><br>
**Install the requirements:** `pip install -r requirements.txt`<br>
<br>
**Run the script:** `python apo.py`<br>
<br>

## Troubleshooting
If files are not moved/renamed it could be that script was unable to determine when the photo was taken, or it could be that the script was able to find GPS metadata but was unable to get a response from OpenMaps and did not rename the file so that it could try again the next time you run the script. 

You can check `apo.log` to determine why any file was not renamed.


