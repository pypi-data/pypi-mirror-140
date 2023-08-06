# test1a
from datetime import datetime
from dayfilter import is_daytime

date_string = '2010-01-01-16:58:30.00000'
date_datetime = datetime.strptime(date_string, '%Y-%m-%d-%H:%M:%S.%f')

# WASHINGTON DC DULLES INT'L AR [STERLING - ISIS], VA. data
latitude = 38.98
longitude = -77.47
time_zone = -5

daytime = is_daytime(date_datetime, latitude, longitude, time_zone)
print(daytime)

# test1b
from dayfilter import DayFilter
import pandas as pd
from datetime import datetime

# WASHINGTON DC DULLES INT'L AR [STERLING - ISIS], VA. data
latitude = 38.98
longitude = -77.47
time_zone = -5

date_strings = [
    '2010-01-01-05:58:42.00000',
    '2010-01-01-06:59:22.00000',
    '2010-01-01-13:22:23.00000',
    '2010-01-01-14:54:55.00000',
    '2010-01-01-15:31:45.00000',
    '2010-01-02-17:12:22.00000',
    '2010-01-02-15:12:32.00000',
    '2010-01-02-16:59:32.00000',
    '2010-01-02-18:00:11.00000',
]
date_format = '%Y-%m-%d-%H:%M:%S.%f'
date_datetimes = [datetime.strptime(date_string, date_format) for date_string in date_strings]

df = pd.DataFrame(index=date_datetimes, data=[1,2,3,4,5,6,7,8,9])

f = DayFilter(latitude, longitude, time_zone)
df_ = f.filter(df)
print(df_)

# test1c
from dayfilter import DayFilter
from dayfilter.post_process import shift_sr_down, shift_ss_up
from dayfilter.logic import logic_daytime

f2 = DayFilter(latitude, longitude, time_zone, post_processes=[shift_sr_down, shift_ss_up], logic=logic_daytime)

df__ = f2.filter(df)
print(df__)
