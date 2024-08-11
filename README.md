## WithJean Scraper

### Overview
This project is designed to scrape product data from the website [With Jean](https://withjean.com) across various categories such as dresses, tops, bottoms, and more. The script utilizes Selenium for navigating the website and BeautifulSoup for parsing the HTML content. The following details are scraped for each product:

- **Product Title**
- **Size**
- **Price**
- **Category**
- **Stock Status**

The extracted data is saved into a CSV file for further analysis or use.

### Features
- **Web Scraping**: Automates the process of gathering product data from the website.
- **Multiple Categories**: Scrapes data across various predefined categories.
- **Data Storage**: Saves the extracted data into a CSV file.
- **Automated Navigation**: Uses Selenium to automate browsing and interaction with the website.

### Prerequisites
- Python 3.x
- Web Driver (GeckoDriver for Firefox)
- An internet connection to access the target website.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Muhammad-Ilyas-Ibrahim/WithJean-Scraper.git
   cd WithJean-Scraper
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Ensure that the GeckoDriver is installed and accessible in your system's PATH, or provide its location in the script.

2. Run the script:
   ```bash
   python main.py
   ```

3. The script will automatically navigate the website, extract product data, and save it to `output.csv`.

### Contributing
Feel free to fork the project and submit pull requests. Any contributions, whether it's fixing bugs, improving documentation, or adding new features, are welcome!
