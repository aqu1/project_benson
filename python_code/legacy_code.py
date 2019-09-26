### Here's a pretty suboptimal approach to scraping the mta site that we tried.  Works, it's just kind of a hack.
prefix = 'http://web.mta.info/developers/'
filename = os.path.expanduser('~') + '/' 'mta-3months.txt'
os.remove(filename)
with open(
    filename, 'a', encoding='utf-8'
) as fh:
    mta_3months = slice(36, 36+16, 1)
    links = soup.body.find_all('a')[mta_3months]
    first_with_header = requests.get(prefix + links.pop(0).get('href')).content.decode('utf-8')
    fh.write(first_with_header + '\n')
    for link in links:
        content = requests.get(prefix + link.get('href')).content.decode('utf-8')
        fh.write(content.split('\n', 1)[1])

## a suboptimal approach to getting the turnstile data per collection hour.
## creates a sum per hour, with obvious failure points between days / turnstiles
## lacks the cleanup routines that were illustrated in the Benson presentation.

import pandas as pd
import os
df = pd.read_csv(os.path.expanduser('~') + '/' + 'mta-3months.txt')

lowerCols = [i.lower().strip() for i in df.columns]
#change control area variable to a more intutive name
lowerCols[0]= 'control_area'
df.columns = lowerCols
df['date_time'] = df.date + ' ' + df.time
df['dt'] = pd.to_datetime(df['date_time'])

df.index = df.dt
df.index
df.columns

df.drop(['date','time','date_time','dt'],inplace=True,axis=1)

df.sort_index(inplace=True)

df['prev_entries']=df.groupby(['unit','scp'])['entries'].transform(lambda x: x.shift(1))
df['entry_change'] = df.entries - df.prev_entries

df['prev_exits']=df.groupby(['unit','scp'])['exits'].transform(lambda x: x.shift(1))
df['exit_change'] = df.exits - df.prev_exits
df.sort_values(by=['control_area','scp'], inplace=True)
df.head(50)
df['min'] = df.index.minute
df['hour'] = df.index.hour
df = df[(df['min'] == 0) ]
