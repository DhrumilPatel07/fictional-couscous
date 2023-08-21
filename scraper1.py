import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
product_data = []
num_pages = 20

for page_num in range(1, num_pages + 1):

    url = f"{base_url}&page={page_num}"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    product_containers = soup.find_all("div", class_="s-result-item")

    for container in product_containers:
        product_url_element = container.find("a", class_="a-link-normal")
        if product_url_element:
            product_url = product_url_element.get("href")
        else:
            product_url = None

        product_name_element = container.find("span", class_="a-text-normal")
        if product_name_element:
            product_name = product_name_element.text.strip()
        else:
            product_name = "Product Name Not Available"

        product_price_element = container.find("span", class_="a-offscreen")
        if product_price_element:
            product_price = product_price_element.text.strip()
        else:
            product_price = "Product Price Not Available"

        rating_tag = container.find("span", class_="a-icon-alt")
        if rating_tag:
            rating = rating_tag.text.split()[0]
        else:
            rating = "Not available"

        num_reviews_tag = container.find("span", {"aria-label": "customer reviews"})
        if num_reviews_tag:
            num_reviews = num_reviews_tag.text.split()[0]
        else:
            num_reviews = "0"

        product_data.append({
            "Product URL": product_url,
            "Product Name": product_name,
            "Product Price": product_price,
            "Rating": rating,
            "Number of Reviews": num_reviews
        })

df = pd.DataFrame(product_data)

df.to_csv("amazon_product_list.csv", index=False)


# Part-2 Function to scrape additional information from a product URL
def scrape_product_details(url1):
    response1 = requests.get(url1)
    soup1 = BeautifulSoup(response1.content, "html.parser")

    # Extract product details
    description = soup1.find("meta", {"name": "description"})["content"]
    asin = soup1.find("th", text="ASIN").find_next("td").text.strip()
    product_description = soup1.find("h2", text="Product description").find_next("p").text.strip()
    manufacturer = soup1.find("th", text="Manufacturer").find_next("td").text.strip()

    return {
        "Description": description,
        "ASIN": asin,
        "Product Description": product_description,
        "Manufacturer": manufacturer
    }


df = pd.read_csv("amazon_product_list.csv")

for index, row in df.iterrows():
    product_url = row["Product URL"]
    additional_info = scrape_product_details(product_url)

    df.at[index, "Description"] = additional_info["Description"]
    df.at[index, "ASIN"] = additional_info["ASIN"]
    df.at[index, "Product Description"] = additional_info["Product Description"]
    df.at[index, "Manufacturer"] = additional_info["Manufacturer"]

df.to_csv("amazon_product_details.csv", index=False)
