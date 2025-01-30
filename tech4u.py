from scrapper import Scrapper
import time
from selenium.webdriver.common.by import By

class ScrapeTech4U(Scrapper):
    
    def get_product_links(self):
        
        product_links = []
        
        products_xml_url = self.web_url + "/product-sitemap.xml"
        
        self.driver.get(products_xml_url)
        
        product_links_eles = self.driver.find_elements(
            By.XPATH, "//table[@id='sitemap']/tbody/tr/td/a[@href]"
        )
        
        for link_ele in product_links_eles:
            
            link = link_ele.get_attribute("href")
            
            if link == "https://tech4u.pk/shop/":
                continue
            
            print(link)
            
            product_links.append(link)
        
        return product_links
    
    def fetch_product_name(self):
    
        summary_ele = self.driver.find_element(
        By.CLASS_NAME, "summary-inner"
        )
        
        product_name = summary_ele.find_element(
            By.CLASS_NAME, "product_title entry-title wd-entities-title".replace(" ", ".")
        ).text
        
        return product_name
    
    def fetch_price(self):
    
        try:
    
            price = self.driver.find_element(
                By.XPATH, "//div[@class='summary-inner']/p[@class='price']/span[@class='woocommerce-Price-amount amount']/bdi"
            )
            
        except:
            
            price = self.driver.find_element(
                By.XPATH, "//div[@class='summary-inner']/p[@class='price']"
            )
        
        return price.text
    
    def fetch_description(self):
    
        try:
            description = self.driver.find_element(
                By.XPATH, "//div[@class='summary-inner']/div[@class='woocommerce-product-details__short-description']/ul"
            )
        except:
            description = self.driver.find_element(
                By.XPATH, "//div[@id='tab-description']/div[@class='wc-tab-inner']"
            )
            
        description = description.text.strip()
        
        return description
    
    def fetch_image_url(self):
        
        image_url = self.driver.find_element(
            By.XPATH, "//div[@class='product-image-wrap']/figure[@class='woocommerce-product-gallery__image']/a"
        ).get_attribute("href")
        
        return image_url
    
    def is_stock_available(self):
    
        stock_available_ele = self.driver.find_elements(
            By.XPATH, "//div[@class='col-12']/div[@class='product-labels labels-rounded']/div[@class='out-of-stock product-label']"
        )
        
        if not stock_available_ele:
            return True
        
        return False
    
    def fetch_category_sub_category(self):
        
        category_eles = self.driver.find_elements(
            By.XPATH, "//div[@class='wd-breadcrumbs']/nav[@class='woocommerce-breadcrumb']/a"
        )
        
        category = {"category": None, "sub_category": None}
        
        for i, category_ele in enumerate(category_eles):
            
            if category_ele.text in ["Home"] or not category_ele.text:
                continue

            if not category["category"]:
                category["category"] = category_ele.text.strip()
                
            elif not category["sub_category"]:
                category["sub_category"] = category_ele.text.strip()
                break

        return category
    
    def fetch_varients(self):
    
        varients = []
        
        try:
            varients_ele_parent = self.driver.find_element(
                By.XPATH, "//div[@class='summary-inner']/form[@class='variations_form cart wd-reset-side-lg wd-reset-bottom-md wd-label-top-md']/table[@class='variations']/tbody/tr/td[@class='value cell with-swatches']"
            )
        except:
            return varients
        
        varients_eles = varients_ele_parent.find_element(
            By.CLASS_NAME, "wd-swatches-single wd-swatches-product wd-bg-style-1 wd-text-style-1 wd-dis-style-1 wd-size-default wd-shape-round".replace(" ", ".")
        ).find_elements(
            By.TAG_NAME, "div"
        )
        
        for varient in varients_eles:
            
            varient_name = varient.get_attribute("data-title")
            
            varient_details = {
                "varient_name" : varient_name
            }
            
            varients.append(varient_details)
        
        return varients
    
    def fetch_product_details(self, link):
        
        self.driver.get(link)
        time.sleep(5)
        
        product_name = self.fetch_product_name()
        price = self.fetch_price()
        image_url = self.fetch_image_url()
        description = self.fetch_description()
        varients = self.fetch_varients()
        stock_available = self.is_stock_available()
        category = self.fetch_category_sub_category()
        
        return {
            "product_name" : product_name,
            "sale_price" : price,
            "image_url" : image_url,
            "description" : description,
            "varients" :varients,
            "stock_availabilty" : stock_available,
            "product_link" : link,
            "category" : category.get("category"),
            "sub_category" : category.get("sub_category") if category.get("sub_category") else category.get("category")
        }
