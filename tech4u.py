import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
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
    ("Apple", "Mac", {"change_category" : True}),
    ("Apple", "iPhone", {"change_category" : True}),
    ("Apple", "iPad", {"change_category" : True}),
    ("Apple", "Apple Watches", {"change_category" : True}),
    ("Apple", "Apple Accessories", {"change_category" : True}),
    ("Microsoft", "Microsoft Pro & Laptop Studio", {"change_category" : True}),
    ("Microsoft", "Microsoft Surface Accessories", {"change_category" : True}),
    ("Samsung", "Samsung Tab", {"change_category" : True}),
    ("Samsung", "Samsung Galaxy Buds", {"change_category" : True}),
    ("Samsung", "Samsung Accessories", {"change_category" : True}),
    ("Amazon", "Amazon Kindle E-Book Reader", {"change_category" : True}),
    ("Amazon", "Amazon TV Device", {"change_category" : True}),
    ("Smart Watches", "Samsung Galaxy Watches", {"change_category" : True}),
    ("Smart Watches", "Huawei Watches", {"change_category" : True}),
    ("Smart Watches", "Zeblaze", {"change_category" : True}),
    ("Smart Watches", "Fitbit Watches", {"change_category" : True}),
    ("Smart Watches", "Amazfit Watches", {"change_category" : True}),
    ("Smart Watches", "Haylou", {"change_category" : True}),
    ("Smart Watches", "Kieslect", {"change_category" : True}),
    ("Smart Watches", "Joyroom Smart Watches", {"change_category" : True}),
    ("Smart Watches", "Xiaomi", {"change_category" : True}),
    ("Audio", "Anker", {"change_category" : True}),
    ("Audio", "Aukey", {"change_category" : True}),
    ("Audio", "Joyroom", {"change_category" : True}),
    ("Audio", "JBL", {"change_category" : True}),
    ("Audio", "Harmon Kardon", {"change_category" : True}),
    ("Audio", "Marshall", {"change_category" : True}),
    ("Audio", "Tronsmart Speakers", {"change_category" : True}),
    ("Accessories", "Adapters", {"change_category" : True}),
    ("Accessories", "Battery Bank", {"change_category" : True}),
    ("Accessories", "Car Charger", {"change_category" : True}),
    ("Accessories", "Connectors", {"change_category" : True}),
    ("Accessories", "Charging Cables", {"change_category" : True}),
    ("Accessories", "Laptop | Mobile Stand/Holder", {"change_category" : True}),
    ("Accessories", "Smart TV Device", {"change_category" : True}),
    ("WiWu", "WiWu Keyboards", {"change_category" : True}),
    ("WiWu", "WiWU Connectors | Hubs", {"change_category" : True}),
    ("WiWu", "WiWu Chargers", {"change_category" : True}),
    ("WiWu", "WiWu PowerBank", {"change_category" : True}),
    ("WiWu", "WiWu Microphone", {"change_category" : True}),
    ("WiWu", "WiWu Airtag", {"change_category" : True}),
    ("WiWu", "Wiwu Car Accessories", {"change_category" : True})
    
]

def fetch_product_name(driver):
    
    summary_ele = driver.find_element(
        By.CLASS_NAME, "summary-inner"
    )
    
    product_name = summary_ele.find_element(
        By.CLASS_NAME, "product_title entry-title wd-entities-title".replace(" ", ".")
    ).text
    
    return product_name

def fetch_price(driver):
    
    try:
    
        price = driver.find_element(
            By.XPATH, "//div[@class='summary-inner']/p[@class='price']/span[@class='woocommerce-Price-amount amount']/bdi"
        )
        
    except:
        
        price = driver.find_element(
            By.XPATH, "//div[@class='summary-inner']/p[@class='price']"
        )
    
    return price.text

def fetch_description(driver):
    
    try:
        description = driver.find_element(
            By.XPATH, "//div[@class='summary-inner']/div[@class='woocommerce-product-details__short-description']/ul"
        )
    except:
        description = driver.find_element(
            By.XPATH, "//div[@id='tab-description']/div[@class='wc-tab-inner']"
        )
        
    description = description.text.strip()
    
    return description

def fetch_image_url(driver):
    
    image_url = driver.find_element(
        By.XPATH, "//div[@class='product-image-wrap']/figure[@class='woocommerce-product-gallery__image']/a"
    ).get_attribute("href")
    
    return image_url

def is_stock_available(driver):
    
    stock_available_ele = driver.find_elements(
        By.XPATH, "//div[@class='col-12']/div[@class='product-labels labels-rounded']/div[@class='out-of-stock product-label']"
    )
    
    if not stock_available_ele:
        return True
    
    return False

def fetch_varients(driver):
    
    varients = []
    
    try:
        varients_ele_parent = driver.find_element(
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

def fetch_product_data(driver, product_link):
    
    driver.get(product_link)
    time.sleep(5)
    
    product_name = fetch_product_name(driver)
    price = fetch_price(driver)
    image_url = fetch_image_url(driver)
    description = fetch_description(driver)
    varients = fetch_varients(driver)
    stock_available = is_stock_available(driver)
    
    return {
        "product_name" : product_name,
        "sale_price" : price,
        "image_url" : image_url,
        "description" : description,
        "varients" :varients,
        "stock_availabilty" : stock_available
    }
    

def check_pagination(driver):
    
    while True:
        
        footer = driver.find_elements(
            By.CLASS_NAME, "wd-loop-footer products-footer".replace(" ", ".")
        )
        
        if not footer:
            break
        
        driver.execute_script("arguments[0].scrollIntoView();", footer[0])
        
        if not footer[0].find_elements(
                By.CLASS_NAME, "btn wd-load-more wd-products-load-more load-on-scroll".replace(" ", ".")
            ):
            break
            
        time.sleep(5)

def get_product_links(driver, product_links):
    
    check_pagination(driver)
    
    page_head = driver.find_element(
        By.CLASS_NAME, "shop-loop-head"
    )
    driver.execute_script("arguments[0].scrollIntoView();", page_head)
    time.sleep(5)
    
    try:
    
        product_cards = driver.find_element(
            By.XPATH, "//div[@class='products elements-grid wd-products-holder  elements-list products-bordered-grid-ins pagination-infinit align-items-start row']"
        ).find_elements(
            By.XPATH, "//div[contains(@class, 'product-grid-item')]"
        )
    except:
        return
        
    for product in product_cards:
        
        product_link = product.find_element(
            By.CLASS_NAME, "product-wrapper"
        ).find_element(
            By.CLASS_NAME, "product-element-top wd-quick-shop".replace(" ", ".")
        ).find_element(
            By.CLASS_NAME, "product-image-link"
        ).get_attribute("href")
        
        print(product_link)
        
        product_links.append(product_link)
    

def move_to_another_category(driver, actions, category, sub_category):
    
    try:
    
        nav_bar_xpath = "//ul[@id='menu-main-header-navigation']/li"
        
        CATEGORY = driver.find_element(
            By.XPATH, f"{nav_bar_xpath}/a[@class='woodmart-nav-link']/span[@class='nav-link-text' and text()='{category}']"
        )
        actions.move_to_element(CATEGORY).perform()
        
        SUB_CATEGORY = driver.find_element(
            By.XPATH, f"{nav_bar_xpath}/div[@class='color-scheme-dark wd-design-default wd-dropdown-menu wd-dropdown']/div[@class='container']/ul/li/a[@class='woodmart-nav-link' and text()='{sub_category}']"
        )
        SUB_CATEGORY.click()
        
        return {
            "success" : True
        }
    
    except Exception as e:
        
        print(traceback.format_exc())
        
        return {
            "success" : False,
            "message" : str(e)
        }

def add_products_to_df(df):
    
    file_path = "tech4u.csv"
    
    try:
        tech4u_df = pd.read_csv(file_path)
    except:
        tech4u_df = pd.DataFrame(
            columns=[
                "Product Name", "Price", "Description", "Varient Name",
                "Stock Availability", "Category", "Sub Category","Image URL"
            ]
        )

    df = df[["Product Name", "Price", "Description", "Varient Name", "Stock Availability", "Category", "Sub Category", "Image URL"]]
    tech4u_df = pd.concat([tech4u_df, df], ignore_index=True)
    
    tech4u_df.to_csv(file_path, index=False)

def scrape_category_data(driver, actions, category, sub_category, change_category=False):
    
    time.sleep(5)
    products = []
    
    if change_category:
        
        response = move_to_another_category(
            driver, actions,
            category, sub_category
        )
        
        if not response.get("success"):
            return response
        
    try:
        
        product_links = []
        get_product_links(driver, product_links)
        
        driver.execute_script("window.open('');")
        time.sleep(3)
        
        driver.switch_to.window(driver.window_handles[1])
        
        for product in product_links:
            
            print(product)
            
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
                "description" : "Description",
                "image_url" : "Image URL",
                "varient_name" : "Varient Name",
                "stock_availabilty" : "Stock Availability"
            }
        )
        
        final_df["Category"] = category
        final_df["Sub Category"] = sub_category
        
        if not "Varient Name" in final_df.columns:
            final_df["Varient Name"] = ""
        
        print(final_df)
        
        add_products_to_df(final_df)
        
        return {
            "success" : True,
            "message" : "Category Data scrapped successfully!"
        }
    
    except Exception as e:
        
        print(traceback.format_exc())
        
        return {
            "success" : False,
            "message" : str(e)
        }

def scrape_all_data():
    
    driver, actions = get_driver()
    driver.get("https://tech4u.pk/")
    
    for params in category_sub_category_lst:
        
        response = scrape_category_data(
            driver, actions,
            params[0], params[1], **params[2]
        )
        
        if not response.get("success"):
            return response
    
    return {
        "success" : True,
        "message" : "Data scrapped successfully!"
    }
    
response = scrape_all_data()
print(response)