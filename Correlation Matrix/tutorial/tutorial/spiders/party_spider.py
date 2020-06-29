import scrapy
import pandas as pd

class PartySpider(scrapy.Spider):
    name = "party"

    def start_requests(self):
        urls= ['https://ballotpedia.org/Partisan_composition_of_governors']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        party_df = pd.DataFrame()
        for i in response.xpath("//table[@id='officeholder-table']/tr"):
            
            office = ""
            party = ""
            
            office=i.xpath('.//td[1]/a/text()').get()
            if office:
                pass
            else:
                office=i.xpath('.//td[1]/text()').get()
                
            off_len = len(office.split(' '))
            office_array = office.split(' ')[-(off_len-2):]
            state = ' '.join(office_array)
                
            party = i.xpath('.//td[3]/text()').get().strip()
            
            element = {
                'Office': office,
                'State': state,
                'Party': party
            }
            
            yield element
            
            party_df = party_df.append(element, ignore_index=True)
            
        party_df = party_df.sort_values('State')
        territories = ['Guam', 'American Samoa', 'the Northern Mariana Islands', 'the U.S. Virgin Islands']
        party_df = party_df[party_df.State != 'Guam']
        party_df = party_df[party_df.State != 'American Samoa']
        party_df = party_df[party_df.State != 'the Northern Mariana Islands']
        party_df = party_df[party_df.State != 'the U.S. Virgin Islands']
                            
        party_df.to_csv('party_df.csv', encoding='utf-8')

    
#        page = response.url.split("/")[-1]
#        filename = f'{page}.html'
#        with open(filename, 'wb') as f:
#            f.write(response.body)
#        self.log(f'Saved file {filename}')