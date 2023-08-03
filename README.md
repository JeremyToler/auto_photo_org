# Automatic Photo Organizer
<br>
I wanted a way to automatically rename and organize photos that are auto-synced to my NAS. This follows the naming scheme I personally  use, but now I can run this with a cronjob once a day instead of using a bulk rename program. 

#### Renaming
Automatically renames photos as follows:
*Year-Month-Day.HourMinuteSecond.City/County.Itter.Ext*

**Some Examples:**
 1\.  2023-07-25.143521.Paris.png
 2\.  2017-10-01.111108.Hawaii_County.png
 3\.  2004-03-20.143659.jpg
 4\.  2006-10-31.jpg
 5\.  2006-10-31(8).jpg

1\. The script will rename the files with as much information as it can, and when possible without the extra number before the extension. 

2\. The script will use the city name if the latitude and longitude GPS metatags line up with a city, otherwise it will use the county name. 

3\. If the script cannot find GPS metadata it will still rename and organize files, but the file names will not include the city/county.

4\. If the script cannot find a timestamp it will attempt to parse one out of the file name. This could result in timestamps that do not include the Hour/Min/Sec. As long as the script can determine the Year/Month/Day it will rename the file. 

5\. If more than one file would have the same name, a number will be added to the end of the file name in parenthesis. 

<br>

#### Organization
Files are moved into folders based on the year the photo was taken.
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
**Edit `config.py`**
unsorted_path: Path to files you want to rename/organize
sorted_path: Folder you want the files to move to
nominatum_agent: Any string you want, just don't leave it blank.
debug_mode: Change to true if you need more info from the debug log.

Install the requirements: `pip install -r requirements.txt`

Run the script: `python apo.py`

<br>

## Troubleshooting
If files are not moved/renamed it could be that script was unable to determine when the photo was taken, or it could be that the script was able to find GPS metadata but was unable to get a response from Open Maps and did not rename the file so that it could try again the next time you run the script. 

You can check `apo.log` to determine why any file was not renamed. 
