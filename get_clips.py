import csv
from glob import glob
import youtube_dl
import datetime
import subprocess

home_dir = '/home/nastase/socialaction/'
raw_dir = home_dir + 'raw/'
clip_dir = home_dir + 'clips/'

# open csv spreadsheet with clip info--100% dependent on correct spreadsheet structure
with open(home_dir + 'clip_spreadsheet.csv') as f:
    reader = csv.reader(f)
    clip_list = list(reader)

# loop through rows in spreadsheet
#for i in range(1, len(clip_list)):
#for i in [61]:
for i in range(1, len(clip_list))[-1:]:
    label = '_'.join([s.replace('&', '').replace('/', '_').lower() for s in clip_list[i][0].split()])
    url = clip_list[i][2]
    start, end = clip_list[i][5], clip_list[i][6]

    print label, url, start, end

    # check if output file already exists
    existing_fn = glob(clip_dir + label + '_' + str(i) + '_trim.mp4')
    if existing_fn:
        print "Final clip file already exists"
        continue
    elif not existing_fn:
        print "Final clip does not yet exist--proceeding"
        pass

    # download youtube clip
    ydl_opts = {'outtmpl': unicode(raw_dir + label + '_' + str(i) + '.%(ext)s')}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception:
            print "Failed to download {0}".format(label + '_' + str(i))
            continue

    # set filenames and reformat timing    
    input_fn = glob(raw_dir + label + '_' + str(i) + '.*')[0]
    output_fn = clip_dir + label + '_' + str(i) + '_trim.mp4'

    start_hms = [int(s) for s in start.split(':')]
    if len(start_hms) < 3: start_hms.insert(0, 0)
    h, m, s = start_hms
    start_time = datetime.time(h, m, s)

    end_hms = [int(s) for s in end.split(':')]
    if len(end_hms) < 3: end_hms.insert(0, 0)
    h, m, s = end_hms
    end_time = datetime.time(h, m, s)

    # call ffmpeg to cut clip from full video
    cmd = ('ffmpeg -i {0} -ss {1} -to {2} -c:v libx264 -preset slow -crf 22 -strict -2 {3}'.format(
               input_fn, str(start_time), str(end_time), output_fn))

    subprocess.call(cmd, shell=True)
