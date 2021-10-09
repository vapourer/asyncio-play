import urllib.request
import urllib.error
import asyncio
import aiohttp
from time import perf_counter
from datetime import datetime

# Experimentation so far, based on https://bbc.github.io/cloudfit-public-docs/asyncio/asyncio-part-1.html et seq.  Also https://docs.aiohttp.org/en/latest/http_request_lifecycle.html
# I decided to explore asyncio as it appears able safely to cater for a combination of distant http calls and local processing.  I am more aware of the Microsoft async implementation and have read justification of the latter's use in this sort of context, as opposed to a multi-threaded approach, as safer and more straight-forward to implement.
# I did not contemplate a multi-processor approach, but imagine that will become useful for heavy data processing.
# I am aware that I can do more with this, and will try to do so before start of the course.  I became somewhat distracted by aiohttp, and find the speed difference, just as implemented here, startling.  Example console output from below:
# Synchronous time: 6.180028399999999
# Asynchronous time: 2.1956493000000004
# Difference: 3.984379099999999

def january_date_as_string(day: int) -> str:
    date = datetime(2016, 1, day)
    return date.strftime('%d%m%Y')    

def download_report(site: str, date: str):
    try:
        url = 'https://webtris.highwaysengland.co.uk/api/v1.0/reports/Daily?sites=' + site + '&start_date=' + date + '&end_date=' + date + '&page=1&page_size=50'
        report = urllib.request.urlopen(url).read()
        with open('synchronous_' + date, 'w') as file:
            file.write(str(report))
    except urllib.error.HTTPError as ueh:
        print('Error: ' + ueh.reason + '; Code: ' + str(ueh.code))
    except urllib.error.URLError as ueu:
        print('Error: ' + ueu.reason)
        
async def download_report_async(site: str, date: str, session: aiohttp.ClientSession):
    async with session.get('https://webtris.highwaysengland.co.uk/api/v1.0/reports/Daily?sites=' + site + '&start_date=' + date + '&end_date=' + date + '&page=1&page_size=50') as response:
        report = await response.text()
        with open('asyncio_' + date, 'w') as file:
            file.write(report)
                
async def download_reports_async(dates: list):
    async with aiohttp.ClientSession() as session:
        for date in dates:
            await download_report_async('1379', date, session)
    
dates = [january_date_as_string(day) for day in range(1, 32)]

start_time = perf_counter()

for date in dates:
    download_report('1379', date)

end_time = perf_counter()
synchronous_time = end_time - start_time

start_time = perf_counter()

loop = asyncio.get_event_loop()
loop.run_until_complete(download_reports_async(dates))

end_time = perf_counter()
asynchronous_time = end_time - start_time

print('Synchronous time: ' + str(synchronous_time))
print('Asynchronous time: ' + str(asynchronous_time))
print('Difference: ' + str(synchronous_time - asynchronous_time))
