from scrapper import Scrapper
import time
from selenium.webdriver.common.by import By

class ScrapePakRef(Scrapper):
    
    def get_product_links(self):
        
        product_links = []
        
        products_xml_url = self.web_url + "/product-sitemap.xml"
        
        self.driver.get(products_xml_url)
        
        product_links_eles = self.driver.find_elements(
            By.XPATH, "//table[@id='sitemap']/tbody/tr/td/a[@href]"
        )
        
        for link_ele in product_links_eles:
            
            link = link_ele.get_attribute("href")
            
            if link == "https://pakref.com/shop/":
                continue
            
            print(link)
            
            product_links.append(link)
        
        return product_links
    
    def fetch_category_sub_category(self):
        
        category_eles = self.driver.find_elements(
            By.XPATH, "//div[@class='container']/nav[@class='woocommerce-breadcrumb']/a"
        )
        
        category = {"category": None, "sub_category": None}
        
        for i, category_ele in enumerate(category_eles):
            
            if category_ele.text in ["Home", "Shop"] or not category_ele.text:
                continue

            if not category["category"]:
                category["category"] = category_ele.text
                
            elif not category["sub_category"]:
                category["sub_category"] = category_ele.text
                break

        return category
            
    
    def fetch_product_name(self):
    
        product_name = self.driver.find_element(
            By.XPATH, "//div[@class='summary entry-summary']/h1[@class='product_title entry-title']"
        ).text
        
        return product_name
    
    def fetch_price(self):
    
        try:
            
            
            price = self.driver.find_element(
                By.XPATH, "//div[@class='product-actions-wrapper']/div[@class='product-actions tc-init']/p[@class='price']/span[@class='woocommerce-Price-amount amount']/bdi"
            ).text
            
            msrp = 0
            
        except:
            
            try:
                
                price = self.driver.find_element(
                    By.XPATH, "//div[@class='product-actions-wrapper']/div[@class='product-actions tc-init']/p[@class='price']/ins/span[@class='woocommerce-Price-amount amount']/bdi"
                ).text
                
                msrp = self.driver.find_element(
                    By.XPATH, "//div[@class='product-actions-wrapper']/div[@class='product-actions tc-init']/p[@class='price']/del/span[@class='woocommerce-Price-amount amount']/bdi"
                ).text
                
            except:
                
                price = self.driver.find_element(
                    By.XPATH, "//div[@class='product-actions-wrapper']/div[@class='product-actions']/p[@class='price']/span[@class='electro-price']/span[@class='woocommerce-Price-amount amount']/bdi"
                ).text
                
                msrp = 0
        
        return price, msrp
    
    def fetch_description(self):
    
        description = self.driver.find_element(
            By.XPATH, "//div[@class='summary entry-summary']/div[@class='woocommerce-product-details__short-description']"
        ).text
            
        return description
    
    def fetch_image_url(self):
        
        try:
        
            image_url = self.driver.find_element(
                By.XPATH,
                "//div[@class='flex-viewport']/div[@class='woocommerce-product-gallery__wrapper']/div[@class='woocommerce-product-gallery__image flex-active-slide']/a/img"
            ).get_attribute("src")
            
        except:
            
            image_url = self.driver.find_element(
                By.XPATH,
                "//div[@class='woocommerce-product-gallery__wrapper']/div[@class='woocommerce-product-gallery__image']/a/img"
            ).get_attribute("src")
            
        
        return image_url
    
    def is_stock_available(self):
    
        stock_ele = self.driver.find_elements(
            By.XPATH, "//div[@class='product-actions-wrapper']/div[@class='product-actions']/div[@class='availability']/span[@class='electro-stock-availability']/p[@class='stock out-of-stock']"
        )
        
        if stock_ele:
            return False
        
        return True
    
    def fetch_product_details(self, link):
        
        self.driver.get(link)
        time.sleep(3)
        
        product_name = self.fetch_product_name()
        
        try:
            sale_price, msrp = self.fetch_price()
        except:
            sale_price, msrp = 0, 0
            
        description = self.fetch_description()
        stock_availabilty = self.is_stock_available()
        image_url = self.fetch_image_url()
        category = self.fetch_category_sub_category()
        
        return {
            "product_name" : product_name,
            "sale_price" : sale_price,
            "msrp" : msrp,
            "description" : description,
            "stock_availabilty" : stock_availabilty,
            "image_url" : image_url,
            "product_link" : link,
            "category" : category.get("category"),
            "sub_category" : category.get("sub_category") if category.get("sub_category") else category.get("category")
        }
