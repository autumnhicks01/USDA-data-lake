USDA DataLake Project
-------------------

### Use Case 

As a **Production Manager** or **Executive Chef**, having easy access to detailed food data and ingredient lists is essential for making informed decisions about inventory, menu planning, and cost management. This USDA DataLake project automates the process of fetching detailed USDA food data, including product names, brands, and ingredients. With this setup, chefs and managers can:

-   Quickly query food ingredients to find suitable options for recipes, dietary needs, and allergens.
-   Easily filter foods by brand or ingredient to make purchasing decisions, ensuring that the right ingredients are always available.
-   Monitor the latest product information from USDA and suppliers, maintaining up-to-date ingredient lists.
-   Query product prices (when integrated with suppliers' data) to calculate food cost per unit, enabling better cost control and purchasing decisions.

By leveraging AWS Glue and Athena, production managers and executive chefs can query large datasets of food products quickly and efficiently, making this process scalable for larger food operations, such as restaurants, catering, and food manufacturing.

* * * * *

### Overview

The `setup_usda_data_lake.py` script performs the following actions:

-   Fetches USDA food data using the USDA API.
-   Uploads raw JSON data to Amazon S3.
-   Creates an AWS Glue database.
-   Creates a Glue Crawler to automatically detect and create the schema.
-   Configures Amazon Athena for querying data stored in the S3 bucket.

### Prerequisites

Before running the script, ensure you have the following:

-   **USDA API Key**: Obtain your API key by signing up for an account at USDA API.
-   **AWS CLI Installed**: Ensure AWS CLI is configured and authenticated to your AWS account.
-   **IAM Role/Permissions**: Ensure the user or role running the script has the following permissions:
    -   **S3**: `s3:CreateBucket`, `s3:PutObject`, `s3:DeleteBucket`, `s3:ListBucket`
    -   **Glue**: `glue:CreateDatabase`, `glue:CreateTable`, `glue:DeleteDatabase`, `glue:DeleteTable`, `glue:CreateCrawler`
    -   **Athena**: `athena:StartQueryExecution`, `athena:GetQueryResults`

### Steps

#### Step 1: Open CloudShell Console

1.  Go to [AWS Console](https://aws.amazon.com/) and sign into your account.
2.  In the top right, next to the search bar, you'll see a square with a `>_` inside. Click this to open the CloudShell.

#### Step 2: Create the `setup_usda_data_lake.py` file

1.  In the CLI (Command Line Interface), type:

    bash

    `nano setup_usda_data_lake.py`

2.  Copy the contents of the `setup_usda_data_lake.py` file from the repository.
3.  Paste it into the CloudShell window and save it.

#### Step 3: Create the `.env` file

1.  In the CLI, type:

    bash

    `nano .env`

2.  Paste the following line of code into your file, ensuring you swap out with your **USDA API Key**:

    bash

    `USDA_API_KEY=your_usda_api_key`

3.  Save the file.

#### Step 4: Run the script

1.  In the CLI, run:

    bash

    `python3 setup_usda_data_lake.py`

2.  The script will fetch food data and upload it to S3. You will see confirmation in the console once the process completes.

### Fetching Data from the USDA API with Pagination

The `setup_usda_data_lake.py` script fetches data from the USDA Food Data Central API using a paginated approach. This ensures that the script doesn't overwhelm the system or hit API rate limits by attempting to download a large amount of data at once. Instead, it downloads data in smaller chunks, each representing a single page of results.

#### Pagination Details:

-   **Page Size:** The script fetches food items in pages, with each page containing up to 25 food records (set by the `page_size` parameter). You can adjust this if needed, but 25 is the default to balance performance and data retrieval.
-   **Max Pages:** The script is configured to retrieve up to 2000 pages of data, which would equate to fetching approximately 50,000 records (25 items per page). However, **the USDA API may limit the number of pages that can be retrieved**, so it is possible that attempting to access more than 2000 pages may cause the script to fail due to the API's rate limits or pagination restrictions. As a result, **the script will only attempt to fetch up to 2000 pages to ensure reliability and avoid hitting these limits**.

#### Key Points to Remember:

-   The **pagination** prevents downloading large files all at once, ensuring that the data is processed in manageable chunks.
-   The script fetches only the relevant data fields: `foodName`, `brand`, `ingredients`, and `nutrients`, significantly reducing the size of the uploaded data compared to the raw API response.
-   **API Limitations:** Since the USDA API may have a limit on the number of pages or requests that can be made, **it is advisable to monitor the process if you need to adjust the `max_pages` value**. For production purposes, a smaller value for `max_pages` (e.g., 1000 or fewer) could be used to ensure the script remains within safe API usage limits.

If you wish to adjust the number of pages being fetched, you can update the `max_pages` parameter to a lower number (e.g., 1000) to avoid exceeding the USDA API's limitations.

#### Step 5: Manually Check for the Resources

1.  **S3 Bucket**: Go to the S3 service in AWS Console and look for the bucket `usda-analytics-data-lake`.

    -   Inside the bucket, you should see a folder `raw-data`, which contains the file `usda_data.json`.
    -   Click the file to view the JSON data.
2.  **Glue Database**: Check the AWS Glue Console and ensure the database `usda_data_lake` has been created.

#### Step 6: Create the Glue Crawler to Automatically Create the Table

To automatically create a schema for your data in AWS Glue, you can set up a **Glue Crawler**:

1.  **Create a Glue Crawler**:

    -   Go to the **AWS Glue Console**.
    -   In the left sidebar, click **Crawlers**, and then click **Add crawler**.
    -   Name your crawler (e.g., `usda_data_crawler`).
    -   Select **Data stores** as your source, and choose **S3** as the data store.
    -   Specify the **S3 path** where the `usda_data.json` file is stored in your `raw-data` folder (e.g., `s3://usda-analytics-data-lake/raw-data/usda_data.json`).
    -   Choose **Glue Data Catalog** as the target.
    -   Select the **usda_data_lake** database that was created by the script.
2.  **Run the Glue Crawler**:

    -   After creating the crawler, click **Run crawler**. The crawler will automatically detect the schema of your JSON data and create a table in the Glue Data Catalog.
3.  **Verify the Table in Glue**:

    -   Once the crawler completes, go to the **Tables** section in the Glue Console under the `usda_data_lake` database.
    -   You should see a table named after your crawler (e.g., `usda_data_lake_table`).

#### Step 7: Open Athena and Run SQL Queries

Now that the data is available in S3 and cataloged in AWS Glue, you can use Amazon Athena to run SQL queries on it. Follow these steps:

1.  **Go to Athena**: In the AWS Console, search for and open **Amazon Athena**.

2.  **Select the Database**: In Athena, select the database `usda_data_lake` from the database dropdown.

3.  **Run SQL Queries**: You can now run SQL queries to explore the data. Here are a few sample queries you can use to get started:

    **1) Search for ingredients containing 'vegetable stock' or 'broth' (all brands)**

    sql

    `SELECT *
    FROM usda_data_lake_table
    WHERE foodname LIKE '%VEGETABLE STOCK%' 
        OR '%BROTH%';`

    **2) Search for 'non-fat yogurt' (all brands)**

    sql

    `SELECT *
    FROM usda_data_lake_table
    WHERE foodname LIKE '%NONFAT YOGURT%';`

    **3) Search for 'tomato sauce' (all brands)**

    sql

    `SELECT *
    FROM usda_data_lake_table
    WHERE foodname LIKE '%TOMATO SAUCE%';`

    **4) Search for the ingredient 'sweetened condensed milk' (all brands)**

    sql


    `SELECT *
    FROM usda_data_lake_table
    WHERE ingredients LIKE '%SWEETENED CONDENSED MILK%';`

    **5) Search for 'ketchup' (all brands)**

    sql


    `SELECT *
    FROM usda_data_lake_table
    WHERE foodname LIKE '%kKETCHUP%';`

    **6) Find a specific product and show its full ingredient list**

    sql


    `SELECT *
    FROM usda_data_lake_table
    WHERE foodname = 'PEACH SELTZER';`

#### Step 8: Manually Update or Schedule Periodic Updates

1.  **Manual Update**: You can rerun the script anytime to fetch the latest data from the USDA API. Simply follow Step 4 again.

2.  **Schedule Automatic Updates**: You can schedule the script to run periodically using **AWS Lambda** or **Amazon CloudWatch Events**. This would ensure your S3 data is regularly updated with the latest product information.

* * * * *

### What We Learned

-   **Using AWS Glue and Athena for querying**: This setup demonstrates how to integrate AWS Glue and Athena for storing and querying large datasets.
-   **Automating the ingestion process**: By using AWS Lambda and CloudWatch, you can automate the ingestion of data from APIs into S3, making data more accessible for analysis.
-   **Flexible querying with SQL**: Athena allows flexible querying of data using SQL, making it easier for business users to find relevant food products, brands, and ingredients.
