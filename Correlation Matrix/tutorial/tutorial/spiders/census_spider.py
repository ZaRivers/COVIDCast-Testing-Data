import scrapy
import pandas as pd

class PartySpider(scrapy.Spider):
    name = "census"
        
    def start_requests(self):
#        df = pd.read_csv('../sample-counties.csv')

#        for i in df.index:
#            lower_county = df.iloc[i].county.lower()
#            postal_lower = df.iloc[i]['Postal Code'].lower()
#            lower_county = lower_county.split(' ')
#            lower_county.append(postal_lower)
#            cong_county = '-'.join(lower_county)
#            df.at[i, 'conglomerate_county'] = cong_county
        
#        counties = df['conglomerate_county'].values

        series = pd.read_csv('../counties_series.csv')
        
        counties = [x[1] for x in series.values]
        
        urls= ['https://datausa.io/profile/geo/%s' % county for county in counties]
        #urls= ['https://datausa.io/profile/geo/orange-county-nc']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #census_df = pd.DataFrame()
        statsbox = response.xpath(".//div[@class='profile-stats']")
        stat = statsbox.xpath(".//div[@class='Stat large-text']")
        
        page = response.url.split("/")[-1]
        
        element = {
            'County': page,
            'State': page.split('-')[-1]
        }
        
        for i in stat:
            label = i.xpath("./div[@class='stat-title']/p/text()").get()
            value = i.xpath("./div[@class='stat-value']/p/text()").get()
            
            element[label] = value
            
        yield element
        #census_df.append(element, ignore_index=True)
        
            
# Running with: scrapy crawl census -o all_counties_census.csv
            
