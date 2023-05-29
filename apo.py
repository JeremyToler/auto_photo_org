# TODO Make a nice heading for this code
# TODO How do I read metadata/exif data?
### https://pillow.readthedocs.io/en/stable/reference/ExifTags.html
# TODO Does needed directory exist?
### if os.path.exists('file_path')
# TODO Make the needed directory
### os.mkdir(path to directory)
### https://www.geeksforgeeks.org/create-a-directory-in-python/#
# TODO rename and move the file
### https://stackoverflow.com/questions/2491222/how-to-rename-a-file-using-python
# TODO Test jpg
# TODO Test png
# TODO Test gif
# TODO Test bmp
# TODO Test very old photos
# TODO Add video support
# TODO Test mp4
# TODO Test avi
# TODO Test mkv
# TODO Test very old video
# TODO How do I make a requirements file?
# TODO Make sure readme file has all instructions for working with the code

from os import walk
import PIL

unsorted_path = 'C:\\Users\\Ueno\\Pictures\\test\\unsorted'
sorted_path = 'C:\\Users\\Ueno\\Pictures\\test\\photos'

def get_files(unsorted_path):
    files = []
    for (dirpath, dirnames, filenames) in walk(unsorted_path):
        files.extend(filenames)
        break # Stops walk from adding filenames in subdirectories.
    return files

def get_metadata(file):
    pass

def sort_file(file):
    pass

def needs_manual_sort(file):
    pass

def main():
    for file in get_files(unsorted_path):
        sort_file(f'{unsorted_path}\\{file}')

if __name__ == '__main__':
    main()