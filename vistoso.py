import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
from slugify import slugify

def get_driver():
    options = Options()
    # options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    actions = ActionChains(driver)
    return driver, actions

category_sub_category_lst = [
    ("Jewellery", "925 Silver Nose Pin", {"change_category" : True}),
    ("Jewellery", "Anklet", {"change_category" : True}),
    ("Jewellery", "Best Sellers", {"change_category" : True}),
    ("Jewellery", "Bracelet/Bangle", {"change_category" : True}),
    ("Jewellery", "Earrings", {"change_category" : True}),
    ("Jewellery", "Gold Plated Chains (Brass)", {"change_category" : True}),
    ("Jewellery", "Premium 1 Ct Bridal Sets", {"change_category" : True}),
    ("Jewellery", "Premium Locket Sets", {"change_category" : True}),
    ("Jewellery", "Rings", {"change_category" : True}),
    ("Jewellery", "Unisex Beaded Bracelet", {"change_category" : True}),
]

def get_products_links(driver, product_links):
        
    pagination_element = driver.find_element(By.ID, "site-pagination")
    driver.execute_script("arguments[0].scrollIntoView();", pagination_element)
    time.sleep(5)
    
    limit_element = driver.find_element(By.ID, "limit")
    driver.execute_script("arguments[0].scrollIntoView();", limit_element)
    time.sleep(5)
    
    all_products_div = driver.find_element(
        By.CLASS_NAME, "row row-0 products products-grid grid-5 layout-1 sidebar-active".replace(" ", ".")
    ).find_elements(
        By.CLASS_NAME, "product col-auto active".replace(" ", ".")
    )
    
    for product in all_products_div:
        
        product_link = product.find_element(
            By.TAG_NAME, "form"
        ).find_element(
            By.TAG_NAME, "div"
        ).find_element(
            By.CLASS_NAME, "product__content"
        ).find_element(
            By.CLASS_NAME, "product__details d-flex flex-nowrap justify-content-between".replace(" ", ".")
        ).find_element(
            By.CLASS_NAME, "product__title"
        ).find_element(
            By.CLASS_NAME, "product__link"
        ).get_attribute("href")
        
        product_links.append(product_link)

        
def get_pages(pagination_element):
    
    pages = pagination_element.find_elements(By.CLASS_NAME, "site-pagination")
    
    if pages:
        pages = pages[0].find_element(By.CLASS_NAME, "notranslate d-flex align-items-center justify-content-center".replace(" ", ".")).find_elements(By.TAG_NAME, "li")

        return pages

    else:
        return []
    
def fetch_product_data(driver, product_link):
    
    driver.get(product_link)
    time.sleep(5)
    
    product_content = driver.find_element(
        By.CLASS_NAME, "product-single__content" 
    )
    
    product_name = product_content.find_element(
        By.CLASS_NAME, "product-single__top"
    ).find_element(
        By.CLASS_NAME, "page-header"
    ).find_element(
        By.CLASS_NAME, "title-section"
    ).find_element(
        By.CLASS_NAME, "title-wrapper"
    ).find_element(
        By.CLASS_NAME, "page-title-wrapper"
    ).find_element(
        By.CLASS_NAME, "product_title.product-single__title"
    ).text
    
    product_description = product_content.find_element(
        By.CLASS_NAME, "product-single__middle"
    ).find_element(
        By.CLASS_NAME, "product-single__short"
    ).text
    
    product_price = product_content.find_element(
        By.CLASS_NAME, "product-single__bottom"
    ).find_element(
        By.CLASS_NAME, "product-single__price product-single__price-template--15848689467547__product-template".replace(" ", ".")
    ).find_element(
        By.CLASS_NAME, "product_price"
    ).find_element(
        By.CLASS_NAME, "price ProductPrice-template--15848689467547__product-template".replace(" ", ".")
    ).find_element(
        By.CLASS_NAME, "money"
    ).text
    
    image_link = driver.find_elements(
        By.CLASS_NAME, "zoomImg"
    )[0].get_attribute("src")
    
    product_details = {
        "product_name" : product_name,
        "product_description" : product_description,
        "product_price" : product_price,
        "stock_availablity" : True,
        "image_link" : image_link
    }
    
    return product_details
    
def fetch_data_from_next_page(driver, page, url, product_links):
    
    page_url = url + "?page={}".format(page)
    driver.get(page_url)
    time.sleep(5)
    
    get_products_links(driver, product_links)
    
def add_products_to_df(df):
    
    file_path = "vistoso.csv"
    
    try:
        vistoso_df = pd.read_csv(file_path)
    except:
        vistoso_df = pd.DataFrame(
            columns=[
                "Product Name", "Price", "Description",
                "Stock Availability", "Category", "Sub Category", "Image URL"
                ]
        )

    df = df[["Product Name", "Price", "Description", "Stock Availability", "Category", "Sub Category", "Image URL"]]
    vistoso_df = pd.concat([vistoso_df, df], ignore_index=True)
    
    vistoso_df.to_csv(file_path, index=False)

def change_sub_category(driver, sub_category):
    
    try:
    
        driver.get("https://www.vistoso.pk/collections")
        driver.implicitly_wait(50)
        
        driver.find_element(By.XPATH, f"//span[text()='{sub_category}']").click()
        
    except Exception as e:
        return {
            "success" : False,
            "message" : str(e)
        }
    
    return {
        "success" : True
    }

def scrape_category_data(driver, category, sub_category, change_category=False):
    
    products = []
    
    if change_category:
        response = change_sub_category(driver, sub_category)
        
        if not response.get("success"):
            return {
                "success" : False,
                "message" : "Failed to change sub category : {}".format(response.get("message"))
            }
    
    try:
        current_page_url = driver.current_url
        product_links = []
        
        get_products_links(driver, product_links)
        
        pagination_element = driver.find_element(By.ID, "site-pagination")
        pages = get_pages(pagination_element)
        
        if pages:
            
            total_pages = len(pages)
            
            for i in range(total_pages):
                
                if i in [0, 1]:
                    continue
                
                fetch_data_from_next_page(driver, i, current_page_url, product_links)
        
        driver.execute_script("window.open('');")
        time.sleep(1)
        
        driver.switch_to.window(driver.window_handles[1])
        
        for product in product_links:
            
            product_details = fetch_product_data(
                driver, product
            )
            
            products.append({
                "Product Name" : product_details.get("product_name"),
                "Price" : product_details.get("product_price"),
                "Description" : product_details.get("product_description"),
                "Stock Availability" : product_details.get("stock_availablity"),
                "Category" : category,
                "Sub Category" : sub_category,
                "Image URL" : product_details.get("image_link")
            })
        
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        products_df =  pd.DataFrame(products)
        add_products_to_df(products_df)
    
        return {
            "success" : True,
            "message" : "Category Data stored successfully!"
        }
        
    except Exception as e:
        return {
            "success" : False,
            "message" : str(e)
        }
        

def scrape_all_data():
    
    driver, actions = get_driver()
    driver.get("https://www.vistoso.pk/")
    
    for params in category_sub_category_lst:
        response = scrape_category_data(driver, params[0], params[1], **params[2])
        
        if not response.get("success"):
            return response


response = scrape_all_data()
print(response)