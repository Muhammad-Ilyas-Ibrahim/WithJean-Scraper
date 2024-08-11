from bs4 import BeautifulSoup
import csv
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager

# Base URL
base_url = "https://withjean.com"

# Categories
categories = [
    "/collections/dresses",
    "/collections/tops",
    "/collections/bottoms",
    "/collections/tees-tanks",
    "/collections/swimwear",
    "/collections/accessories",
    "/products/gift-card"
]

# Helper functions
def wait_for_element(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))

def get_input_quantity_selector(driver):
    element = wait_for_element(driver, ".js-qty__wrapper input", By.CSS_SELECTOR)
    return element.get_attribute('id')

def get_fieldset_selector(driver):
    element = wait_for_element(driver, "fieldset.variant-input-wrap", By.CSS_SELECTOR)
    return element.get_attribute('id')

def clear_cart(driver):
    driver.get(base_url+'/cart')
    CartNotCleared = True
    selector = "#MainContent > div > div > div > form > div:nth-child(2) > div > div.grid__item.medium-up--three-fifths > div > div.grid__item.three-quarters > p:nth-child(3) > a.btn.btn--secondary.btn--small.small--hide"
    while CartNotCleared:
        clear_cart = wait_for_element(driver, selector, By.CSS_SELECTOR)
        if clear_cart:
            clear_cart.click()
        else:
            CartNotCleared = False

def select_size_and_checkout(driver, size, fieldset_id):
    size_selectors = {
        "XXS": f"#ProductSelect-{fieldset_id}-option-0 > div:nth-child(1)",
        "XS": f"#ProductSelect-{fieldset_id}-option-0 > div:nth-child(2)",
        "S": f"#ProductSelect-{fieldset_id}-option-0 > div:nth-child(3)",
        "M": f"#ProductSelect-{fieldset_id}-option-0 > div:nth-child(4)",
        "L": f"#ProductSelect-{fieldset_id}-option-0 > div:nth-child(5)",
        "XL": f"#ProductSelect-{fieldset_id}-option-0 > div:nth-child(6)"
    }

    if size in size_selectors:
        size_element = wait_for_element(driver, size_selectors[size], By.CSS_SELECTOR)
        size_element.click()
        print("Size Selected")
        sleep(1)
    else:
        print(f"Size {size} not found!")
        return

    add_to_cart_button = wait_for_element(driver, f"#AddToCart-{fieldset_id}", By.CSS_SELECTOR)
    add_to_cart_button.click()
    print("Add to cart button clicked!")
    sleep(1)
    
    product_in_cart_already = None
    try:
        product_in_cart_already = driver.find_element( By.CSS_SELECTOR, f'#AddToCartForm-{fieldset_id} > div.errors.text-center')
    except:
        pass
    if product_in_cart_already:
        print("Cart need to be cleared")
        clear_cart(driver)
        print("Cart cleared")
        
    sleep(3)
    while True:
        try:
            agree_checkbox = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "CartAgree")))
            ActionChains(driver).move_to_element(agree_checkbox).click().perform()
            print("Agree checkbox clicked!")
            break
        except:
            sleep(1)
                
    quantity_id = get_input_quantity_selector(driver)
    quantity_element = wait_for_element(driver, quantity_id, By.ID)
    quantity_element.send_keys("1000")
    # sleep(3)

    checkout_button = wait_for_element(driver, "#CartContainer > div.drawer__footer > button", By.CSS_SELECTOR)
    checkout_button.click()
    
    # Stock available
    span_css_selector = ".product__status.product__status--reduced .page-main__emphasis"
    span_element = wait_for_element(driver, span_css_selector, By.CSS_SELECTOR)
    span_value = span_element.text
    
    remove_from_cart = wait_for_element(driver, "body > div.content > div > div > main > div.step > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td.product__status.product__status--reduced > form > button", By.CSS_SELECTOR)
    remove_from_cart.click()
    
    something_went_wrong = False
    try:
        find_error = driver.find_element(By.CSS_SELECTOR, 'body > div > div.content > div:nth-child(1) > div > p')
        find_error = find_error.text
        if str(find_error).lower() == 'something went wrong.':
            something_went_wrong = True
    except:
        pass
    if something_went_wrong:
        print("Cart need to be cleared")
        clear_cart(driver)
        print("Cart cleared")
        
    return span_value

def get_product_details_from_pagination_pages(driver, page_url):
    product_urls = []
    driver.get(page_url)

    products_loaded = wait_for_element(driver, '#CollectionSection', By.CSS_SELECTOR)
    sleep(1)
    print("Products Loaded ")
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract product URLs
    product_divs = soup.find_all('div', class_='grid-product--image')

    product_urls = [base_url + div.find('a')['href'] for div in product_divs]
    product_urls = list(set(product_urls))
    print(f"Products Scrapped from {page_url}: {len(product_urls)}")

    return list(set(product_urls))

# Function to get all product URLs from a category page, including pagination
def get_product_urls(driver, category_url):
    product_urls = []
    page_url = base_url + category_url
    
    driver.get(page_url)

    products_loaded = wait_for_element(driver, '#CollectionSection > div.grid.grid--uniform.grid--collection.boost-pfs-filter-products > div:nth-child(1) > div > div.grid-product__image-mask > div:nth-child(2) > div > div > div > div.grid-product--image.slick-slide.slick-current.slick-active > a > div > img', By.CSS_SELECTOR)
    print("Products Loaded ")
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract product URLs
    for a_tag in soup.select('a.grid-product__link'):
        print(f"Product URLs Scrapped: {len(product_urls)}", end="\r")
        product_urls.append(base_url + a_tag['href'])

    # Check for next page
    pagination = soup.find('div', class_='boost-pfs-filter-bottom-pagination')

    # Extracting all URLs
    try:
        urls = [a['href'] for a in pagination.find_all('a', href=True)]
    except:
        urls = [a['href'] for a in pagination.find('a', href=True)]
    for url in list(set(urls)):
        print("Getting Product URLs from: ", url)
        product_urls += get_product_details_from_pagination_pages(driver, url)
        
    product_urls = list(set(product_urls))
            
    return product_urls

def extract_product_details(driver, product_url, category):
    driver.get(product_url)
    check_page_loaded = wait_for_element(driver, "#MainContent" , By.CSS_SELECTOR)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Product name
    product_name = soup.select_one('h2.product-single__title').get_text(strip=True)

    # Product price
    try:
        product_price = soup.select_one('#ProductPrice').get_text(strip=True)
    except:
        product_price = "N/A"
        
    # Available sizes
    available_sizes = []
    default_sizes = ['XXS', 'XS', 'S', 'M', 'L', 'XL']
    for size_input in soup.select('fieldset.variant-input-wrap input'):
        if 'disabled' not in size_input.get('class', []):
            available_sizes.append(size_input['value'])
    
    if not available_sizes:
        available_sizes = ["N/A"]
    else:
        product_with_all_sizes_and_stock = []
        fieldset_id = get_fieldset_selector(driver)
        # print(fieldset_id)
        fieldset_id = str(fieldset_id).split("-")[1]
        for size in default_sizes:
            if size in available_sizes:
                stock = int(select_size_and_checkout(driver, size, fieldset_id))
            else:
                stock = 0
            print(f"Product Name: {product_name} | category: {str(category).split('/').pop()} Size: {size} | Stock : {stock}")
            
            if product_with_all_sizes_and_stock:
                product_with_all_sizes_and_stock[0].append(stock)
            else:
                sizes = ','.join(available_sizes)
                print("Available Sizes: ", sizes)
                product_with_all_sizes_and_stock.append([product_name, str(category).split("/").pop(), product_price, sizes, stock])
            
            if stock != 0:
                driver.get(product_url)
                
    # Check if the file exists
    file_exists = os.path.isfile('products.csv')

    # Open the file in append mode if it exists, else in write mode
    with open('products.csv', mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        # Write header only if the file does not exist
        if not file_exists:
            writer.writerow(["Product Name", "Category", "Price", "Sizes", "XSS", 'XS', 'S', 'M', 'L', 'XL'])
        writer.writerows(product_with_all_sizes_and_stock)
    product_with_all_sizes_and_stock.clear()       

if __name__ == "__main__":
    
    username = os.getlogin()
    
    # Start browser
    options = webdriver.FirefoxOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--disable-infobars')
    options.add_argument("--no-sandbox")
    options.binary_location = f'C:\\Users\\{username}\\AppData\\Local\\Mozilla Firefox\\firefox.exe'
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(options=options, service=service)
    
    driver.get(base_url)
    
    continue_btn = wait_for_element(driver, '/html/body/div[1]/div[1]/div[2]/form/button', By.XPATH)
    if continue_btn:
        continue_btn.click()
    else:
        print("Continue Button Could not be found!")
    
    for index, category in enumerate(categories):
        print(f"Category being scraped: {category.split('/').pop()}")
        product_urls = get_product_urls(driver, category)
        for index, product_url in enumerate(product_urls):
            print(f"{index}/{len(product_urls)} Scrapped from {category.split('/').pop()} Category")
            extract_product_details(driver, product_url, category)
            
    print("Data scraped and saved to products.csv")
    
    driver.quit()
