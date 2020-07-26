import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin

main_url = "http://202.57.13.26:201/"
nomor_id = 0

def login_failed(response):

    # print("failed cuy")
    pass

class scrapMaxim(scrapy.Spider):

    name = "maxim"

    def start_requests(self):
        yield scrapy.http.Request('http://202.57.13.26:201/', self.login_action)

    def login_action(self,response):

        token = response.xpath("//input[@name='action']/@value").extract_first()
       
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'action' : token,
                'signin-username':'transvision',
                'signin-password':'transvision2019'},
            callback=self.logged_in
        )
    
    def logged_in(self, response):
        
        if login_failed(response):
            self.logger.error("Login failed")
            return
        
        return scrapy.http.Request('http://202.57.13.26:201/device',self.parse)
        


    def parse(self,response):
        total_records = response.selector.xpath('//span[@class="records-count"]/text()').get()
        
        max_page = round(int(total_records)/25)
        for i in range( max_page ):
            page = i + 1
            #print("page : ",page)
            next_page = "device?get_table=true&table=table_stb&limit=25&page="+str(page)+"&method=text"
            next_url = urljoin(main_url,next_page)
            #print(next_url)
            yield scrapy.http.FormRequest(url=next_url,callback=self.parse2)

    
    def parse2(self,response):

        all_page_row = response.selector.xpath('//tr[@data-id]')
        for row_page in all_page_row:
            link_mac = row_page.xpath('./td/div/div[@class="device_info"]/a[@class="text-hs-color"]/@href').get()
            link_mac = urljoin(main_url,link_mac)
            dev_id = row_page.xpath('./td/div/div[@class="device_info"]/a[@class="text-hs-color"]/text()').get()
            alias_txt = row_page.xpath('./td/div/div[@class="device_info"]/span[@class="text-muted"]/text()').get()
            channel_txt = row_page.xpath('./td/a[@class="text-hs-color"]/text()').get()

            global nomor_id
            nomor_id += 1


            yield scrapy.Request(link_mac, callback=self.get_mac, meta={'item':{
                'no' : nomor_id,
                'dev-id' : dev_id.strip(),
                'alias' : alias_txt.strip(),
                'channel' : channel_txt.strip(),
            }})

    def get_mac(self,response):
        item = response.meta['item']
        item['mac_address'] = response.xpath('//div/input[@id="mac_address"]/@value').get()
        item['alias_info'] = response.xpath('//div/input[@id="alias"]/@value').get()
        return item

process = CrawlerProcess(settings={
	"FEEDS": {
		"result_gotv.csv": {
			"format": "csv",
		},
	},
})

process.crawl(scrapMaxim)
process.start()