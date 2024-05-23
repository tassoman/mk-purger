""" Misskey Purger """
import time
import os
from datetime import datetime
from misskey import Misskey
from misskey.exceptions import MisskeyAPIException
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()

DELETED_NOTES = 0
DELETED_FILES = 0
RATIO = 0
PAUSE = 2

mk = Misskey(address=os.getenv('MK_HOST'), i=os.getenv('MK_TOKEN'))

def purge_notes(how_many = 1):
    """ Delete attachments and notes from remote timeline"""
    when = datetime.now() - relativedelta(months=2)
    when = int(when.timestamp())
    # print(when)
    time.sleep(PAUSE)
    old_remote = mk.notes_global_timeline(limit=how_many,with_files=True,since_date=when)

    #pylint:disable=global-statement
    for note in old_remote:
        global DELETED_FILES, DELETED_NOTES
        # print(f'\r . N: {note["id"]}', end='', flush=True)
        # print(f'\r . F: {note["fileIds"]}', end='', flush=True)
        for fid in note['fileIds']:
            time.sleep(PAUSE)
            try:
                if mk.drive_files_delete(fid):
                    DELETED_FILES += 1
            except MisskeyAPIException as e:
                print(e)
                if str(e).startswith('RATE_LIMIT_EXCEEDED'):
                    raise KeyboardInterrupt from e

        time.sleep(PAUSE)
        try:
            if mk.notes_delete(note['id']):
                DELETED_NOTES += 1
        except MisskeyAPIException as e:
            print(e)
            if str(e).startswith('RATE_LIMIT_EXCEEDED'):
                raise KeyboardInterrupt from e

# pylint:disable=line-too-long
try:
    while True:
        purge_notes()
        if DELETED_NOTES != 0:
            RATIO = DELETED_FILES / DELETED_NOTES

        print(f'\r . Deleted {DELETED_NOTES} notes and {DELETED_FILES} files (average {RATIO:.2f} files per note).', end='', flush=True)

except KeyboardInterrupt:
    print(' . ')
    print(' . Exit.')
