import requests
import json
import os
from dotenv import load_dotenv
import boto3

load_dotenv()

# Set up your environment variables
api_key = os.getenv("USDA_API_KEY")  
usda_endpoint = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Initialize S3 client
s3_client = boto3.client("s3")
bucket_name = "usda-analytics-data-lake" 
region = "us-east-1"

def fetch_all_food_data(query="*", data_type="Branded", page_size=25, max_pages=2000):
    """Fetch all food data with paginated requests, limiting to a set number of pages."""
    all_data = []
    page_number = 1
    
    while page_number <= max_pages:  
        url = f"{usda_endpoint}?query={query}&dataType={data_type}&pageSize={page_size}&pageNumber={page_number}&sortBy=publishedDate&sortOrder=desc&api_key={api_key}"

        print(f"Fetching page {page_number}...")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('foods'):
                break
          
            for food_item in data.get("foods", []):
                # Parse only the necessary fields: foodName, brand, and ingredients
                food_info = {
                    "foodName": food_item.get("description", "").strip(),
                    "brand": food_item.get("brandOwner", "").strip(),
                    "ingredients": food_item.get("ingredients", "").strip() if food_item.get("ingredients") else "Not available"
                }

                all_data.append(food_info)

            page_number += 1

        except requests.exceptions.RequestException as req_err:
            print(f"Request error: {req_err}")
            break  

    return all_data

def upload_data_to_s3(data):
    """Upload parsed food data to S3."""
    try:
        file_key = "raw-data/usda_data.json"  # S3 path for the data
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json.dumps(data, indent=4)  # Pretty print for better readability
        )
        print(f"Uploaded {len(data)} items to S3: {file_key}")
    except Exception as e:
        print(f"Error uploading data to S3: {e}")

def main():
    print("Fetching all food data...")
    food_data = fetch_all_food_data(query="*")  # Pass your query to get data
    if food_data:
        upload_data_to_s3(food_data)
    else:
        print("No data fetched.")
    print("Data processing and upload complete.")

if __name__ == "__main__":
    main()
