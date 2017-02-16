import scrapy
import dataset

from scrapy.selector import HtmlXPathSelector

db = dataset.connect('sqlite:///iOSDevices.sqlite3')
table = db['devices']

class device():
    device_name = ""
    model_id = ""
    year = ""
    soc = ""
    ram = ""
    mem_speed = ""
    mem_type = ""
    cpu = ""
    cpu_arch = ""
    cpu_data_width = ""
    cpu_cores = ""
    cpu_clock = ""
    cpu_cache_l1 = ""
    cpu_cache_l2 = ""
    cpu_cache_l3 = ""
    motion_coprocessor = ""
    gpu = ""
    gpu_cores = ""
    gpu_clock_speed = ""
    screen_res = ""
    screen_ppi = ""
    screen_size = ""
    latest_ios = ""

def splitChartColumnData(data):
    if data == "":
        return []
    temp = data.strip().replace(" ", "").split("•")
    return temp

def convertTableRowToDevice(row):
    dev = device()
    dev.device_name = row[0]
    dev.model_id = row[1]
    dev.year = row[2]
    dev.soc = row[3]
    dev.ram = row[4]
    dev.mem_speed = row[5]
    dev.mem_type = row[6]
    dev.cpu = row[7]
    dev.cpu_arch = row[8]
    dev.cpu_data_width = row[9]
    dev.cpu_cores = row[10]
    dev.cpu_clock = row[11]
    cacheSplit = splitChartColumnData(row[12])
    if len(cacheSplit) == 0:
        dev.cpu_cache_l1 = "0"
        dev.cpu_cache_l2 = "0"
        dev.cpu_cache_l3 = "0"
    if len(cacheSplit) == 1:
        dev.cpu_cache_l1 = cacheSplit[0]
        dev.cpu_cache_l2 = "0"
        dev.cpu_cache_l3 = "0"
    if len(cacheSplit) == 2:
        dev.cpu_cache_l1 = cacheSplit[0]
        dev.cpu_cache_l2 = cacheSplit[1]
        dev.cpu_cache_l3 = "0"
    if len(cacheSplit) == 3:
        dev.cpu_cache_l1 = cacheSplit[0]
        dev.cpu_cache_l2 = cacheSplit[1]
        dev.cpu_cache_l3 = cacheSplit[2]
    dev.motion_coprocessor = row[13]
    dev.gpu = row[16]
    dev.gpu_cores = row[17]
    dev.gpu_clock_speed = row[18]
    dev.screen_res = row[19]
    dev.screen_ppi = row[20]
    dev.screen_size = row[21]
    dev.latest_ios = row[22]
    return dev

def writeDeviceToDatabase(dev):
    table.insert(dev.__dict__)

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://blakespot.com/ios_device_specifications_grid.html',
    ]

    def parse(self, response):
        sel = response.selector
        table = sel.css("table>tr")
        for tr in table:
            if table.index(tr) == 0:
                continue
            if table.index(tr) == len(table)-1:
                continue
            row = []

            for td in tr.xpath('td'):
                rowContents = ' '.join(td.extract().strip().split())
                rowText = ""
                if rowContents.startswith("<td> <a"):
                    rowText = td.xpath("a/text()").extract()
                else:
                    rowText = td.xpath("text()").extract()

                try:
                    rowText = ' '.join(rowText[0].strip().split())
                except Exception as e:
                    rowText = ''
                row.append(rowText)

            dev = convertTableRowToDevice(row)
            writeDeviceToDatabase(dev)