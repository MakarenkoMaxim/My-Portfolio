import requests as rq
from lxml import html
from datetime import datetime as dt
from section import Section
import pandas as pd
from config import *
import psycopg2
from export_images import export, clear_directory

URL_REAL_COMMERCIAL = "https://www.realcommercial.com.au"
URL_REAL_COMMERCIAL_SOLD = "https://www.realcommercial.com.au/?channel=sold"
URL_REAL_COMMERCIAL_FOR_SAIL = "https://www.realcommercial.com.au/for-sale"
URL_COMMERCIAL_REAL_ESTATE = "https://www.commercialrealestate.com.au/"
URL_DEVELOPMENT_READY = "https://www.commercialrealestate.com.au/"

PROXY = {"https": "random_prop:W0JP4l1rDddjNy@s2.airproxy.io:30110"}


class Scraper:
    def __init__(self):
        self.sections = []
        self.data_time_now = str(dt.now())

    @staticmethod
    def parse_description(tree, xpath):
        i = 0
        result = ""
        while True:
            i += 1
            try:
                result += str(tree.xpath(xpath + f"[{i}]")[0]) + "\n"
            except IndexError:
                break
        return result

    @staticmethod
    def parse_hl(tree, xpath):
        i = 0
        result = ""
        while True:
            i += 1
            try:
                result += str(tree.xpath(xpath + f"[{i}]/text()")[0]) + "\n"
            except IndexError:
                break
        return result

    @staticmethod
    def get_url(url):
        i = 0
        while True:
            i += 1
            if i >= 10:
                return
            try:
                resp = rq.get(url, proxies=PROXY)
                return resp
            except:
                print("try to open page again...\n")

    def parse_real_commercial_urls(self):
        for path in [URL_REAL_COMMERCIAL_FOR_SAIL, URL_REAL_COMMERCIAL_SOLD]:
            site = self.get_url(path)
            tree = html.fromstring(site.content)

            areas_path = "/html/body/main/div/div[3]/div[3]/div[2]/div/div"
            for i in range(1, 7):
                res = tree.xpath(areas_path + f"/div[{i}]/a")[0].attrib['href'].split('/')
                self.sections.append(Section(res[-3], res[-2], f"{path}/{res[-2]}".replace('?channel=', '')))

    def try_page(self, section, page):
        url = None
        try:
            url = self.sections[section].url + f"/?page={page}"
            response = self.get_url(url)
            block_path = '//*[@id="wrapper"]/div/div[3]/div/div[2]/div[1]'

            tree = html.fromstring(response.content)
            result = tree.xpath(block_path)[0]
            return True, url, tree

        except IndexError:
            return False, url, None

    def save_info(self):
        items = []
        for section in self.sections:
            for item in section.key_info:
                items.append(item)

        filename = f"outputs/{self.data_time_now} (parsing results).csv".replace(':', '.')
        df = pd.DataFrame(items).groupby("id").first()
        df.to_csv(filename, sep=';', index=False, float_format='%.f', encoding='utf8')

        return items

    def sql_insert(self, items, last_count):
        items = items[last_count:]
        connection = None
        query = ""

        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )

            connection.autocommit = True
            print("\n[INFO] connection opened.")

            for item in items:
                data_dictionary = {}
                for column in item:
                    if column != 'id':
                        if column == 'return':
                            sql_column = '_return_'
                        else:
                            sql_column = column.replace(' ', '_')
                            sql_column = sql_column.replace('(', '')
                            sql_column = sql_column.replace(')', '')
                        data_dictionary.update({sql_column: item[column]})

                keys = 'date_time_index, '
                values = f"'{self.data_time_now}',"

                for i in data_dictionary:
                    keys += f'{i}, '
                    if data_dictionary[i].replace('.', '').replace(',', '').isdigit():
                        values += f"{data_dictionary[i]}, "
                    else:
                        item = str(data_dictionary[i])
                        item = item.replace("'", "`")
                        item = item.replace("\n", "\t")
                        values += f"'{item}', "

                while True:
                    if keys[-1] == ' ' or keys[-1] == ',':
                        keys = keys[:-1]
                    else:
                        break

                while True:
                    if values[-1] == ' ' or values[-1] == ',':
                        values = values[:-1]
                    else:
                        break

                with connection.cursor() as cursor:
                    query = f"INSERT INTO text_outputs ({keys}) VALUES ({values});"
                    cursor.execute(query)
                print("[INFO] insert to database successfully, text information saved.")


        except Exception as ex_:
            print("[!] An error while SQL database using:   ", ex_)
            print("[INFO] ERROR WHILE QUERY EXECUTING:  ", query)

        finally:
            if connection is not None:
                connection.close()
                print("[INFO] connection closed.")

    def get_items(self):

        last_count = 0

        for section in range(len(self.sections)):
            i = 1
            errors = 0
            valid = True
            item_path = ".//div[contains(@class, 'ListingCard_listingCard')]"

            while valid:
                valid, url, tree = self.try_page(section, i)
                if valid is False:
                    break
                for item in tree.xpath(item_path)[0].xpath("//*[@class='Footer_actionBar_1NS8y']/a[1]"):
                    item_name = item.attrib['href']

                    try:

                        item_url = URL_REAL_COMMERCIAL + item_name

                        item = self.get_url(item_url)
                        tree = html.fromstring(item.content)

                        key_info = {}

                        key_info.update({"id": item_name.split('-')[-1]})

                        key_info.update({"section url": self.sections[section].url})
                        key_info.update({"property id": item_name.split('-')[-1]})
                        key_info.update({"property url": item_url})
                        key_info.update({"channel": self.sections[section].url.split('/')[3]})
                        key_info.update({"property location": self.sections[section].area})

                        xpath_address = "//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[1]/div/div[1]/div[1]/h1/span/text()"
                        address = tree.xpath(xpath_address + "[1]")[0] + ", " + tree.xpath(xpath_address + "[3]")[0]

                        p_name1 = address.split(',')[0]

                        symbol = 0
                        for s in range(len(address)):
                            if address[s] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                                symbol = s
                                break

                        p_name2 = address[:symbol]

                        if len(p_name1) < len(p_name2):
                            property_name = p_name1
                        else:
                            property_name = p_name2
                        address = address.replace(property_name, '')

                        key_info.update({"property name": property_name})
                        key_info.update({"property address": address})

                        xpath_property_type = "//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/text()"
                        property_type = tree.xpath(xpath_property_type)[0]
                        key_info.update({"property type": str(property_type)})

                        xpath_last_updated = "//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[4]/div[1]/div/p/span[2]/text()[2]"
                        last_updated = tree.xpath(xpath_last_updated)[0]
                        key_info.update({"last updated": str(last_updated)})

                        xpath_method_of_sale = "//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div/text()"
                        method_of_sale = tree.xpath(xpath_method_of_sale)[0]
                        key_info.update({"price information (1)": str(method_of_sale.split(',')[-1])})

                        xpath_date_related = "//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/p/text()"
                        date_related = tree.xpath(xpath_date_related)[0]
                        key_info.update({"price information (2)": str(date_related)})

                        info_num = 0
                        while True:
                            info_num += 1
                            xpath_info = f"//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[1]/div/div[3]/div/div[{info_num}]/button/p/text()"
                            xpath_title = f"//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[1]/div/div[3]/div/div[{info_num}]/div/p/text()"

                            try:
                                info = tree.xpath(xpath_info)[0]
                                title = str(tree.xpath(xpath_title)[0]).lower()
                                if title == "land area" or title == "floor area":
                                    key_info.update({title: str(info).split(' ')[0]})
                                    key_info.update({title + " unit": str(info).split(' ')[-1]})
                                else:
                                    key_info.update({title: str(info)})

                            except:
                                break

                        xpath_headline = "//*[@class='PrimaryDetailsBottom_headline_3oTbK']/text()"
                        headline = tree.xpath(xpath_headline)[0]
                        key_info.update({"headline": str(headline)})

                        xpath_description = "//*[@class='DescriptionPanel_description_20faq']/text()"
                        xpath_highlights = "//*[@class='PrimaryDetailsBottom_highlights_Q76Ym']/li"

                        description = self.parse_description(tree, xpath_description)
                        highlights = self.parse_hl(tree, xpath_highlights)

                        key_info.update({"description": str(description)})
                        key_info.update({"highlights": str(highlights)})

                        try:
                            xpath_status = "//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/text()"
                            status = tree.xpath(xpath_status)[0]
                            key_info.update({"status": str(status)})
                        except:
                            key_info.update({"status": ""})

                        images = tree.xpath("//*[@class='GalleryItem_photoButton_1WIQ9']/img")

                        src = ""
                        for image in images:
                            current_src = f"{image.attrib['src']}"
                            src += f"\"{current_src}\", "

                            res = self.get_url(current_src)
                            outputs_path = f"outputs/{self.data_time_now} (property, id={key_info['property id']}).jpg"
                            with open(outputs_path.replace(':', '.'), 'wb') as outfile:
                                outfile.write(res.content)

                        key_info.update({"images": src[:-2]})

                        try:
                            video_id = str(tree.xpath("//img[contains(@src,'img.youtube.com')]/@src")[0]).split('/')[-2]
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            key_info.update({"video url": video_url})
                        except:
                            key_info.update({"video url": ""})

                        xpath_agency_name = "//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[2]/div/div/div[1]/div/h3/a/text()"
                        agency_name = tree.xpath(xpath_agency_name)[0]
                        key_info.update({"agency name": str(agency_name)})

                        try:
                            xpath_agency_logo = ".//img[contains(@class,'BrandingBanner_logo')]/@src"
                            agency_logo = tree.xpath(xpath_agency_logo)[0]
                            key_info.update({"agency logo": str(agency_logo)})

                            res = self.get_url(key_info["agency logo"])
                            outputs_path = f"outputs/{self.data_time_now} (agency logo, name={key_info['agency name']}).jpg"
                            with open(outputs_path.replace(':', '.'), 'wb') as outfile:
                                outfile.write(res.content)

                        except:
                            key_info.update({"agency logo": ""})

                        xpath_agency_address = "//*[@id='wrapper']/div/div[3]/div[5]/div[1]/div[1]/div[2]/div/div/div[1]/div/address/text()"
                        agency_address = str(tree.xpath(xpath_agency_address)[0]) + ", " + str(
                            tree.xpath(xpath_agency_address + '[2]')[0])
                        key_info.update({"agency address": agency_address})
                        key_info.update({"agency state": agency_address.split(' ')[-2]})
                        key_info.update({"agency city": agency_address.split(',')[-2].replace(' ', '')})

                        xpath_agents = ".//h4[contains(@class,'AgentDetails_name')]/text()"
                        agents_names = ""
                        for agent in tree.xpath(xpath_agents):
                            agents_names += agent + ", "
                        key_info.update({"agents names": agents_names[:-2]})

                        xpath_agents_telephones = ".//a[contains(@class,'AgentDetails_button')]/span/text()"
                        agent_telephones = []
                        for telephone in tree.xpath(xpath_agents_telephones):
                            agent_telephones.append(telephone)

                        agent_telephones_full = ""
                        for telephone in agent_telephones:
                            phone_index = item.text.find(telephone[:-3], 119000)
                            last_symbol = item.text[phone_index:phone_index + 20].find('"')
                            agent_telephones_full += item.text[phone_index:phone_index + last_symbol].replace(' ',
                                                                                                              '') + ", "
                        key_info.update({"agents telephones": agent_telephones_full[:-3]})

                        self.sections[section].key_info.append(key_info)
                        print(f"Item {key_info['property id']} parsed!")


                    except Exception as _ex:
                        print("[!] Have unhandled exception while parsing:  ", _ex)
                        errors += 1
                        continue

                print(f"\n\nPage {i} parsed!\n\n")
                items = self.save_info()
                self.sql_insert(items, last_count)
                export(self.data_time_now)
                clear_directory()
                last_count = len(items)

                print("\n")

                if errors >= 5:
                    break

                i += 1
