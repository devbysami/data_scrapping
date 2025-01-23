import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
from slugify import slugify
import traceback

def get_driver():
    options = Options()
    options.headless = True
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    actions = ActionChains(driver)
    return driver, actions


category_sub_category_lst = [
    ("VAPORIZERS", "BOX MOD KITS", {"change_category" : True}),
    ("VAPORIZERS", "MODS", {"change_category" : True}),
    ("VAPORIZERS", "POD MOD", {"change_category" : True}),
    ("VAPORIZERS", "MECHANICALS", {"change_category" : True}),
    ("VAPORIZERS", "PODS", {"change_category" : True}),
    ("E-LIQUIDS", "FRUITY E-LIQUIDS", {"change_category" : True}),
    ("E-LIQUIDS", "FRUITY ICED E-LIQUID", {"change_category" : True}),
    ("E-LIQUIDS", "DESSERTS E-LIQUIDS", {"change_category" : True}),
    ("E-LIQUIDS", "TOBACCO E-LIQUID", {"change_category" : True}),
    ("SALT NICS", "SALT NICS", {"change_category" : True}),
    ("VAPE ACCESSORIES", "REPLACEMENT COILS", {"change_category" : True}),
    ("VAPE ACCESSORIES", "POD CARTRIDGES", {"change_category" : True}),
    ("VAPE ACCESSORIES", "BATTERIES", {"change_category" : True}),
    ("VAPE ACCESSORIES", "CHARGERS", {"change_category" : True}),
    ("VAPE ACCESSORIES", "COTTON", {"change_category" : True}),
    ("VAPE ACCESSORIES", "REBUILDABLE TOOLS", {"change_category" : True}),
    ("VAPE ACCESSORIES", "REPLACEMENT GLASS", {"change_category" : True}),
    ("TANKS", "RDA", {"change_category" : True}),
    ("TANKS", "RTA", {"change_category" : True}),
    ("TANKS", "SUB-OHM TANKS", {"change_category" : True}),
    ("DISPOSABLES", "DISPOSABLES", {"change_category" : True}),
    ("KUIT", "KUIT", {"change_category" : True}),
    ("JUUL", "JUUL", {"change_category" : True}),
]

def check_pagination(driver):
    
    time.sleep(5)
    
    while True:
        
        pagination_ele = driver.find_elements(
            By.CLASS_NAME, "pagination-page-item pagination-page-infinite".replace(" ", ".")
        )
        
        if not pagination_ele:
            break
        
        if pagination_ele[0].find_elements(
                By.CLASS_NAME, "button button--secondary disabled".replace(" ", ".")
            ):
            break
            
        pagination_ele[0].find_element(
            By.CLASS_NAME, "button button--secondary".replace(" ", ".")
        ).click()
        
        time.sleep(3)

def get_products_links(driver, products_links):
    
    check_pagination(driver)
    
    limit_element = driver.find_element(
        By.CLASS_NAME, "toolbar-dropdown limited-view hidden-on-mobile".replace(" ", ".")
    )
    driver.execute_script("arguments[0].scrollIntoView();", limit_element)
    time.sleep(3)
    
    product_cards = driver.find_element(
        By.ID, "main-collection-product-grid"
    ).find_elements(
        By.CLASS_NAME, "product"
    )
    
    for product in product_cards:
        
        product_link_ele = product.find_element(
            By.TAG_NAME, "div"
        ).find_element(
            By.CLASS_NAME, "card"
        ).find_element(
            By.CLASS_NAME, "card-product"
        ).find_element(
            By.CLASS_NAME, "card-product__wrapper"
        )
        
        try:
            product_link = product_link_ele.find_element(
                By.CLASS_NAME, "card-media card-media--portrait media--hover-effect media--loading-effect".replace(" ", ".")
            ).find_element(
                By.CLASS_NAME, "card-link"
            ).get_attribute("href")
            
        except:
            product_link = product_link_ele.find_element(
                By.CLASS_NAME, "card-media card-media--portrait media--loading-effect".replace(" ", ".")
            ).find_element(
                By.CLASS_NAME, "card-link"
            ).get_attribute("href")
        
        
        print(product_link)
        
        products_links.append(product_link)

def fetch_price(driver):
    
    product_price_ele = driver.find_element(
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

def fetch_varients(driver):
    
    varients = []
    
    try:
        varients_ele = driver.find_element(
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
            
            varient_name = driver.find_element(
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

def fetch_description(driver):
    
    description = driver.find_element(
        By.ID, "tab-description-mobile"
    ).text
    
    return description.strip()

def fetch_product_name(driver):
    
    product_name = driver.find_element(
        By.XPATH, "//div[@class='productView-top']/div[@class='halo-productView-right productView-details clearfix']/div/div[@class='productView-moreItem']/h1[@class='productView-title']/span"
    ).text
    
    return product_name

def fetch_image_url(driver):
    
    image_url = driver.find_element(
        By.CLASS_NAME, "productView-image productView-image-adapt fit-unset slick-slide slick-current slick-active".replace(" ", ".")
    ).find_element(
        By.CLASS_NAME, "productView-img-container product-single__media".replace(" ", ".")
    ).find_element(
        By.CLASS_NAME, "media"
    ).find_element(
        By.TAG_NAME, "img"
    ).get_attribute("src")
    
    return image_url

def fetch_product_data(driver, product_link):
    
    print(product_link)
    
    driver.get(product_link)
    time.sleep(5)
    
    product_name = fetch_product_name(driver)
    sale_price, msrp = fetch_price(driver)
    varients = fetch_varients(driver)
    description = fetch_description(driver)
    image_url = fetch_image_url(driver)
    
    return {
        "product_name" : product_name,
        "sale_price" : sale_price,
        "msrp" : msrp,
        "varients" : varients,
        "description" : description,
        "image_url" : image_url
    }

def move_to_another_category(driver, actions, category, sub_category):
    
    try:
        
        driver.get("https://www.kingvape.pk/")
    
        try:
            
            CATEGORY = actions.move_to_element(driver.find_element(
                By.XPATH, f"//ul[@class='list-menu list-menu--inline text-left']/li[@class='menu-lv-item menu-lv-1 text-left no-megamenu dropdown']/a/span[@class='text p-relative' and text()='{category}']"
            )).perform()
            
            time.sleep(5)
            
        except Exception as e:
            
            CATEGORY = driver.find_element(
                By.XPATH, f"//ul[@class='list-menu list-menu--inline text-left']/li[@class='menu-lv-item menu-lv-1 text-left no-megamenu']/a/span[@class='text p-relative' and text()='{category}']"
            )
            CATEGORY.click()
            
            return {
                "success" : True,
                "message" : "Category changed successfully!"
            }
        
        if category == "E-LIQUIDS":
            
            SHOP_BY = actions.move_to_element(
                driver.find_element(By.XPATH, "//div[@class='site-nav-list-dropdown']/a/span[@class='text p-relative' and text()='SELECT BY FLAVOR']")
            ).perform()
            
            time.sleep(5)
            sub_category_xpath = f"//li[@class='menu-lv-item menu-lv-3 text-left']/a/span[@class='text p-relative' and text()='{sub_category}']"
            
        else:
            sub_category_xpath = f"//li[@class='menu-lv-item menu-lv-2 text-left  ']/a/span[@class='text p-relative' and text()='{sub_category}']"
        
        SUB_CATEGORY = driver.find_element(
            By.XPATH, sub_category_xpath
        )
        SUB_CATEGORY.click()
    
        return {
                "success" : True,
                "message" : "Category changed successfully!"
            }
        
    except Exception as e:
        return {
            "success" : False,
            "message" : str(e)
        }
    
def add_products_to_df(df):
    
    file_path = "kingvape.csv"
    
    try:
        kingvape_df = pd.read_csv(file_path)
    except:
        kingvape_df = pd.DataFrame(
            columns=[
                "Product Name", "Price", "MSRP", "Description","Varient Name",
                "Stock Availability", "Category", "Sub Category","Image URL"
                ]
        )

    df = df[["Product Name", "Price", "MSRP", "Description", "Varient Name", "Stock Availability", "Category", "Sub Category", "Image URL"]]
    kingvape_df = pd.concat([kingvape_df, df], ignore_index=True)
    
    kingvape_df.to_csv(file_path, index=False)

def scrape_category_data(driver, actions, category, sub_category, change_category=False):
    
    products = []
    time.sleep(5)
    
    try:
        AGE_VERIFICATION = driver.find_element(By.ID, "verify-age").click()
    except Exception as e:
        pass
    
    if change_category:
        print("THIS IS CATEGORY>>>>>>>>>>>", category)
        print("THIS IS SUB CATEGORY>>>>>>>>>>>", sub_category)
        response = move_to_another_category(driver, actions, category, sub_category)
        
        if not response.get("success"):
            return {
                "success" : False,
                "message" : "Failed to change sub category : {}".format(response.get("message"))
            }
    
    try:
    
        product_links = []
        get_products_links(driver, product_links)
        
        driver.execute_script("window.open('');")
        time.sleep(3)
        
        driver.switch_to.window(driver.window_handles[1])
        
        for product in product_links:
            
            product_details = fetch_product_data(
                driver, product
            )
            print(product_details)
            products.append(product_details)
                
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        products_df = pd.DataFrame(products)
        
        if products_df.empty:
            return {
                "success" : True,
                "message" : f"No Products found for this category {category} - {sub_category}"
            }
        
        df_exploded = products_df.explode('varients', ignore_index=True)
        varients_df = pd.json_normalize(df_exploded['varients'])
        final_df = df_exploded.drop(columns=['varients']).join(varients_df)
                
        final_df = final_df.rename(
            columns={
                "product_name" : "Product Name",
                "sale_price" : "Price",
                "msrp" : "MSRP",
                "description" : "Description",
                "image_url" : "Image URL",
                "varient_name" : "Varient Name",
                "stock_availabilty" : "Stock Availability"
            }
        )
        
        final_df["Category"] = category
        final_df["Sub Category"] = sub_category
        
        if not "Stock Availability" in final_df.columns:
            final_df["Stock Availability"] = ""
            
        if not "Varient Name" in final_df.columns:
            final_df["Varient Name"] = ""
        
        add_products_to_df(final_df)
        
        return {
            "success" : True,
            "message" : "Category Data stored successfully!"
        }
        
    except Exception as e:
        
        print(traceback.format_exc())
        return {
            "success": False,
            "message" : str(e)
        }
        
def scrape_all_data():
    
    driver, actions = get_driver()
    driver.get("https://www.kingvape.pk/")
    
    for params in category_sub_category_lst:
        
        response = scrape_category_data(
            driver, actions, params[0], params[1], **params[2]
        )
        print(response)
        if not response.get("success"):
            return response
        
    df = pd.read_csv("kingvape.csv")
    df = df.drop_duplicates(subset='Product Name')
    df = df.to_csv("kingvape.csv", index=False)
    
    return {
        "success" : True,
        "message" : "Data scrapped successfully!"
    }
        
response = scrape_all_data()
print(response)