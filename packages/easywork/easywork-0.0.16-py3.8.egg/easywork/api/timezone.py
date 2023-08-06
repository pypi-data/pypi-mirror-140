from easywork.util.request import get
from easywork.util.time import strptime

BEIJING_TIME_URL = 'http://time1909.beijing-time.org/time.asp'


def get_beijing_time():
    try:
        data = get(BEIJING_TIME_URL).text.split(';')
        nyear = data[1].split('=')[1]
        nmonth = data[2].split('=')[1]
        nday = data[3].split('=')[1]
        nhrs = data[5].split('=')[1]
        nmin = data[6].split('=')[1]
        nsec = data[7].split('=')[1]
        return strptime(f'{nyear}-{nmonth}-{nday} {nhrs}:{nmin}:{nsec}', '%Y-%m-%d %H:%M:%S')
    except:
        return None
