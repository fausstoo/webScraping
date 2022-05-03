import scrapy
from scrapy import signals
from pydispatch import dispatcher
import json
import time

class hemnetSpider(scrapy.Spider):
    name = 'hemnet'
    start_urls = ['https://www.hemnet.se/bostader?item_types%5B%5D=bostadsratt']
    counter = 0
    results = {}
    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def parse(self, response):
        for ad in response.css("ul.normal-results > li.normal-results__hit > a::attr('href')"):
            time.sleep(2)
            yield scrapy.Request(url=ad.get(), callback=self.parseInnerPage)
        nextPage = response.css("a.next_page::attr('href')").get()
        if nextPage is not None:
            time.sleep(2)
            response.follow(nextPage, self.parse)
    def parseInnerPage(self, response):
        street_name = response.css("h1.qa-property-heading::text").get()
        price = response.css("p.property-info__price::text").get()
        price = price.replace("kr", "")
        price = price.replace(u"\xa0", "")

        attrData = {}
        for attrs in response.css("div.property-attributes > div.property-attributes-table > dl.property-attributes-table__area > div.property-attributes-table__row"):
            attrLabel = attrs.css("dt.property-attributes-table__label::text").get()
            if attrLabel is not None:
                attrLabel = attrLabel.replace(u"\n", "")
                attrLabel = attrLabel.replace(u"\t", "")
                attrLabel = attrLabel.replace(u"\xa0", "")
                attrLabel = attrLabel.strip()
            attrValue = attrs.css("dd.property-attributes-table__value::text").get()
            if attrValue is not None:
                attrValue = attrValue.replace(u"\n", "")
                attrValue = attrValue.replace(u"\t", "")
                attrValue = attrValue.replace(u"\xa0", "")
                attrValue = attrValue.strip()
            if attrLabel is not None:
                attrData[attrLabel] = attrValue
        self.results[self.counter] = {
            "street_name":street_name,
            "price":price,
            "attrs":attrData
            }
        self.counter = self.counter + 1

    def spider_closed(self, spider):
        with open('results.json', 'w') as fp:
            json.dump(self.results, fp)