from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import re
import xml.etree.ElementTree as ET


def scroll_page(driver):
    for _ in range(8):
        driver.execute_script("window.scrollBy(0, 2000)")
        sleep(6)


def get_page_source():
    for i in range(1, 3):
        driver = webdriver.Chrome()
        driver.maximize_window()
        url = f'https://www.farfetch.com/ca/shopping/women/dresses-1/items.aspx?page={i}'
        driver.get(url)
        sleep(4)
        scroll_page(driver)
        html_content = driver.page_source
        with open(f"page-{i}.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        driver.close()


def scrape_page():
    products = []
    g = 0
    for i in range(1, 3):
        with open(f"page-{i}.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        sleep(2)
        soup = BeautifulSoup(html_content, "html.parser")
        sleep(2)
        product_cards = soup.find_all('div', attrs={"itemid": True})
        for card in product_cards:
            g += 1
            print(g)
            item_id = card['itemid']
            store_id = re.search(r'storeid=(\d+)', item_id).group(1)
            id = re.search(r'item-(\d+)\.aspx', item_id).group(1)
            brands = [brand.text for brand in card.find_all(attrs={"data-component": "ProductCardDescription"})]
            prices = [price.text for price in card.find_all(attrs={"data-component": "Price"})]
            descriptions = [description.text for description in
                            card.find_all(attrs={"data-component": "ProductCardDescription"})]
            titles = [title.text for title in card.find_all(attrs={"data-component": "ProductCardInfoClamp"})]
            image_elements = card.find_all("img")
            image_links = [img["src"] for img in image_elements]
            a_elements = card.find_all(attrs={"data-component": "ProductCardLink"})
            href_list = ["https://www.farfetch.com" + a["href"] for a in a_elements]
            availability = [availability.text for availability in
                            card.find_all(attrs={"data-component": "ProductCardSizesLabel"})]
            sizes = [size.text for size in card.find_all(attrs={"data-component": "ProductCardSizesAvailable"})]

            product_data = {
                'id': id,
                'item_group_id': store_id,
                'brands': brands,
                'prices': prices,
                'descriptions': descriptions,
                'titles': titles,
                'image_links': image_links,
                'href_list': href_list,
                'availability': availability,
                'sizes': sizes
            }

            products.append(product_data)
            sleep(3)  # Add delay to avoid being blocked by the website

    return products


def generate_xml(data_list):
    channel = ET.Element("channel")
    description = ET.SubElement(channel, "description")
    description.text = "Product Catalog"

    for data in data_list:
        item = ET.SubElement(channel, "item")

        id_element = ET.SubElement(item, "id")
        id_element.text = data['id']

        if data.get('item_id'):
            item_id = ET.SubElement(item, "item_id")
            item_id.text = data['item_id']

        if data.get('brands'):
            brand = ET.SubElement(item, "brand")
            brand.text = ', '.join(data['brands'])

        if data.get('prices'):
            price = ET.SubElement(item, "price")
            price.text = ', '.join(data['prices'])

        if data.get('descriptions'):
            description = ET.SubElement(item, "description")
            description.text = ', '.join(data['descriptions'])

        if data.get('titles'):
            title = ET.SubElement(item, "title")
            title.text = ', '.join(data['titles'])

        if data.get('image_links'):
            image_link = ET.SubElement(item, "image_link")
            image_link.text = ', '.join(data['image_links'])

        if data.get('href_list'):
            link = ET.SubElement(item, "link")
            link.text = ', '.join(data['href_list'])

        if data.get('availability'):
            availability = ET.SubElement(item, "availability")
            availability.text = ', '.join(data['availability'])

        if data.get('sizes'):
            size = ET.SubElement(item, "size")
            size.text = ', '.join(data['sizes'])

    tree = ET.ElementTree(channel)
    tree.write("output.xml", encoding='utf-8', xml_declaration=True)


def main():
    get_page_source()
    sleep(5)
    scraped_data = scrape_page()
    generate_xml(scraped_data)


if __name__ == "__main__":
    main()
