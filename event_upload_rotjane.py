"""04.10.17
For interacting with Rotational Jane database:
to upload events from event folders as quakeml files 
attach .png and .json files to each quakeml through REST format
"""
import re
import os
import sys
import glob
import requests
import datetime

# settings 
root_path = 'http://127.0.0.1:8000/rest/'
authority = ('chow','chow')
OUTPUT_path = './'

# for attachments
head_p1 = {'content-type': 'image/png',
                 'category': 'Event Information'} 
head_p2 = {'content-type': 'image/png',
                 'category': 'Waveform Comparison'} 
head_p3 = {'content-type': 'image/png',
                 'category': 'Correlation/Backazimuth'} 
head_p4 = {'content-type': 'image/png',
                 'category': 'P-Coda Comparison'} 
headers_json = {'content-type': 'text/json',
                 'category': 'Processed Data'} 

# converter for datetime object to file naming format i.e. 20XX-XX-XX (hacky)
timeconvert = lambda time: '{}-{}-{}'.format(time.year,str(time.month).zfill(2),
                                                        str(time.day).zfill(2))

# EITHER look for events in the past week
cat = []
for J in range(7):
    past = datetime.datetime.utcnow() - datetime.timedelta(days=J)
    day = glob.glob(OUTPUT_path+'GCMT_{}*'.format(timeconvert(past)))
    cat += day

# OR grab all folder names and sort by time with newest events first
# cat = glob.glob(OUTPUT_path+'GCMT*/')
# cat.sort(reverse=True)
# ============================================================================

error_list,error_type = [],[]
for event in cat:
    try:
        os.chdir(event)
        attachments = glob.glob('*')

        # check: full folder
        if len(attachments) < 6:
            error_list.append(event)
            error_type.append('Attachment Number Too Low: {}'.format(
                                                            len(attachments)))
            os.chdir('..')
            continue

        # assign attachments (kinda hacky)
        for J in attachments:
            if '.json' in J:
                json = J
            elif '.xml' in J:
                xml = J
            elif '_page_1.png' in J:
                page1 = J
            elif '_page_2.png' in J:
                page2 = J
            elif '_page_3.png' in J:
                page3 = J
            elif '_page_4.png' in J:
                page4 = J
            else:
                error_list.append(event)
                error_type.append('Unidentified Attachment: {}'.format(J))

        # push quakeml file
        with open(xml,'rb') as fh:
            r = requests.put(
                url=root_path + 'documents/quakeml/{}'.format(xml),
                auth=authority,
                data=fh)

        # check: already uploaded (409) and check for incomplete folders
        if r.status_code == 409:
            r2 = requests.get(
                url=root_path + 'documents/quakeml/{}'.format(xml),
                auth=authority)
            assert r2.ok
            att_count = r2.json()['indices'][0]['attachments_count']

            if att_count == 5:
                os.chdir('..')
                continue
            elif att_count != 5:
                error_list.append(event)
                error_type.append('Already Uploaded; Attachment Count Error')
                os.chdir('..')
                continue

        assert r.ok

        # find attachment url
        r = requests.get(
                url=root_path + 'documents/quakeml/{}'.format(xml),
                auth=authority)
        assert r.ok

        attachment_url = r.json()['indices'][0]['attachments_url']

        # post image attachments            
        for pngs,heads in zip([page1,page2,page3,page4],
                                [head_p1,head_p2,head_p3,head_p4]):
            with open(pngs,'rb') as fhp:
                r = requests.post(
                    url=attachment_url,
                    auth=authority,
                    headers=heads,
                    data=fhp)

            assert r.ok

        # post .json
        with open(json,'rb') as fhj:
            r = requests.post(
                url=attachment_url,
                auth=authority,
                headers=headers_json,
                data=fhj)

            assert r.ok

        os.chdir('..')

    except ConnectionError:
        error_list.append(event)
        error_type.append('Connection Error')
        os.chdir('..')
        continue

    except AssertionError:
        # if assertion fails for any reason, delete current folder
        print(r.content)
        r_del = requests.delete(
                url=root_path + 'documents/quakeml/{}'.format(xml),
                auth=authority)
        error_list.append(event)
        error_type.append(r.content)
        os.chdir('..')
        continue

# write error log to txt file to see what files failed, timestamp for uniqueness
if len(error_list) > 0:
    timestamp = datetime.datetime.now()
    JD = timestamp.day
    H = timestamp.hour
    M = timestamp.minute
    S = timestamp.minute
    with open('errorlog_{}-{}{}{}.txt'.format(JD,H,M,S),'w') as f:
        f.write('Error Log Created on {}\n'.format(timestamp))
        for i in range(len(error_list)):
            f.write('{}\t{}\n'.format(error_list[i],error_type[i]))
    print('Created '+'errorlog_{}-{}{}{}.txt'.format(JD,H,M,S) +
            ' with {} errors'.format(len(error_list)))



# from IPython.core.debugger import Tracer; Tracer(colors="Linux")()
