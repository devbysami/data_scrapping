from scrapper import Scrapper
import time
from selenium.webdriver.common.by import By

class ScrapeFloyd(Scrapper):
    
    def get_product_links(self):
        
        product_links = []
        
        products_xml_url = self.web_url + "/catalog/seo_sitemap/product/"
        self.driver.get(products_xml_url)
        
        pages = int(self.driver.find_elements(
            By.XPATH, "//div[@class='page-sitemap']/div[@class='pages']/a[@class='last' and @href]"
        )[0].text)
        
        for i in range(pages):
            
            next_page_url = products_xml_url + f"?p={i + 1}"
            self.driver.get(next_page_url)
            
            product_links_eles = self.driver.find_elements(
                By.XPATH, "//div[@class='page-sitemap']/ul[@class='sitemap']/li/a[@href]"
            )
            
            for link_ele in product_links_eles:
                
                link = link_ele.get_attribute("href")
                print(link)
                
                product_links.append(link)
        
        return product_links
    
    def fetch_category_sub_category(self, soup):
        
        category_eles = soup.select("div.breadcrumbs a[href]")
        category = {"category": None, "sub_category": None}
        
        for ele in category_eles:
            text = ele.get_text(strip=True)
            
            if text == "Home" or not text:
                continue
            
            if not category["category"]:
                category["category"] = text
                
            elif not category["sub_category"]:
                category["sub_category"] = text
                break
            
        return category
    
    def fetch_product_name(self, soup):
        return soup.select_one('div.product-name h1').get_text(strip=True)
    
    def fetch_price(self, soup):
        return soup.select_one('span.price').get_text(strip=True)
    
    def is_stock_available(self, soup):
        availability = soup.select_one('p:contains("Availability: ") span').get_text(strip=True)
        return availability.lower() == "in stock"
    
    def fetch_description(self, soup):
        return soup.select_one('div.short-description').get_text(strip=True)
    
    def fetch_image_url(self, soup):
        return soup.select_one("div.product-image a img.product-retina")["src"]
    
    def fetch_product_details(self, link):
        
        soup = self.fetch_page_content(link)
        
        product_name = self.fetch_product_name(soup)
        price = self.fetch_price(soup)
        description = self.fetch_description(soup)
        stock_available = self.is_stock_available(soup)
        image_url = self.fetch_image_url(soup)
        category = self.fetch_category_sub_category(soup)
        
        return {
            "product_name" : product_name,
            "price" : price,
            "description" : description,
            "stock_availability" : stock_available,
            "product_link" : link,
            "image_url" : image_url,
            "category" : category.get("category") if category.get("category") else "Clothing",
            "sub_category" : category.get("sub_category") if category.get("sub_category") else category.get("category")
        }