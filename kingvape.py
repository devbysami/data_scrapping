from scrapper import Scrapper
import time
from selenium.webdriver.common.by import By

class ScrapeKingVape(Scrapper):
    
    def get_product_links(self):
                
        products_xml_url = self.web_url + "/sitemap_products_1.xml?from=7974072975541&to=8149449834677"
        
        soup = self.fetch_page_content(products_xml_url)
        
        product_links = [loc.text for loc in soup.find_all("loc") if loc.text.startswith("https://www.kingvape.pk/products/")]
        
        return product_links
            
    
    def fetch_product_name(self):
    
        product_name = self.driver.find_element(
            By.XPATH, "//div[@class='productView-top']/div[@class='halo-productView-right productView-details clearfix']/div/div[@class='productView-moreItem']/h1[@class='productView-title']/span"
        ).text
    
        return product_name
    
    def fetch_price(self):
    
        product_price_ele = self.driver.find_element(
            By.XPATH, "//div[@class='productView-top']/div[@class='halo-productView-right productView-details clearfix']/div/div[@class='productView-moreItem']/div[@class='productView-price no-js-hidden clearfix']/div/dl"
        )
        
        sale_price = product_price_ele.find_element(
            By.CLASS_NAME, "price__regular"
        ).find_element(
            By.CLASS_NAME, "price__last"
        ).find_element(
            By.TAG_NAME, "span"
        ).text
        
        if not sale_price:
            
            sale_price = product_price_ele.find_element(
                By.CLASS_NAME, "price__sale"
            ).find_element(
                By.CLASS_NAME, "price__last"
            ).find_element(
                By.TAG_NAME, "span"
            ).text
        
        msrp = product_price_ele.find_element(
            By.CLASS_NAME, "price__sale"
        ).find_element(
            By.CLASS_NAME, "price__compare"
        ).find_element(
            By.TAG_NAME, "s"
        ).text
        
        if not msrp:
            msrp = 0
        
        
        return sale_price, msrp
    
    def fetch_description(self):
    
        description = self.driver.find_element(
            By.ID, "tab-description-mobile"
        ).text
        
        return description.strip()
    
    def fetch_image_url(self):
    
        image_url = self.driver.find_element(
            By.CLASS_NAME, "productView-image productView-image-adapt fit-unset slick-slide slick-current slick-active".replace(" ", ".")
        ).find_element(
            By.CLASS_NAME, "productView-img-container product-single__media".replace(" ", ".")
        ).find_element(
            By.CLASS_NAME, "media"
        ).find_element(
            By.TAG_NAME, "img"
        ).get_attribute("src")
        
        return image_url
    
    def fetch_varients(self):
    
        varients = []
        
        try:
            varients_ele = self.driver.find_element(
                By.XPATH, "//div[@class='productView-top']/div[@class='halo-productView-right productView-details clearfix']/div/div[@class='productView-moreItem productView-moreItem-product-variant']/div/div/variant-radios/fieldset"
            )
        except:
            return varients
        
        varients_lables = varients_ele.find_elements(By.TAG_NAME, "label")
        
        for varient in varients_lables:
            
            try:
                
                varient_name = varient.find_element(
                    By.CLASS_NAME, "text"
                ).text
                
            except:
                
                varient_id = varient.get_attribute("data-variant-id")
                
                varient_name = self.driver.find_element(
                    By.XPATH, f"//fieldset[@class='js product-form__input product-form__swatch clearfix']/input[@data-variant-id='{varient_id}']"
                ).get_attribute("value")
            
            if varient.get_attribute("class") == 'product-form__label soldout':
                stock_availabilty = False
            
            else:
                stock_availabilty = True
                
            varient_details = {
                "varient_name" : varient_name,
                "stock_availabilty" : stock_availabilty
            }
            varients.append(varient_details)
        
        return varients
    
    def fetch_product_data(self, product_link):
    
        print(product_link)
        
        self.driver.get(product_link)
        time.sleep(5)
        
        product_name = self.fetch_product_name()
        sale_price, msrp = self.fetch_price()
        varients = self.fetch_varients()
        description = self.fetch_description()
        image_url = self.fetch_image_url()
        
        return {
            "product_name" : product_name,
            "sale_price" : sale_price,
            "msrp" : msrp,
            "varients" : varients,
            "description" : description,
            "image_url" : image_url
        }
