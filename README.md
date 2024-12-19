# IPO Alert System

This project scrapes Initial Public Offering (IPO) data from [Moneycontrol.com](https://www.moneycontrol.com/ipo/open-upcoming-ipos/), calculates the minimum funds required to apply for upcoming Mainboard IPOs, and sends notifications via Pushbullet.

## Features

*   **Web Scraping:** Scrapes IPO data (company name, issue price, lot size, open/close dates, etc.) from the Moneycontrol website using `requests` and `BeautifulSoup`.
*   **Fund Calculation:** Calculates the minimum funds required to apply for all Mainboard IPOs closing in the next 7 days, considering that you can apply on any day between the open and close dates.
*   **Pushbullet Notifications:** Sends notifications to your Pushbullet app with:
    *   The minimum fund required for the next 7 days.
    *   Details of each upcoming IPO (open/close dates, issue price, lot size).
*   **Error Handling:** Includes error handling for web requests, HTML parsing, and Pushbullet notifications. Sends error notifications to Pushbullet if something goes wrong.

## Prerequisites

*   **Python 3:** Make sure you have Python 3 installed on your system.
*   **Libraries:** Install the required libraries using pip:

    ```bash
    pip install pandas requests beautifulsoup4 lxml pushbullet.py
    ```
*   **Pushbullet Account:** You'll need a Pushbullet account and an **Access Token**. You can create an account and get your token from the [Pushbullet website](https://www.pushbullet.com/).

## Setup

1. **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```
    (Replace `<repository_url>` with the actual URL of your repository and `<repository_name>` with the name of the directory).

2. **Enter Your Pushbullet Access Token:**
    *   Open the Python script (e.g., `ipo_alert.py`).
    *   Replace `YOUR_PUSHBULLET_ACCESS_TOKEN` with your actual Pushbullet access token:

    ```python
    ACCESS_TOKEN = "YOUR_PUSHBULLET_ACCESS_TOKEN"
    ```

## Usage

1. **Run the Script:**

    ```bash
    python ipo_alert.py
    ```

2. **Notifications:**
    *   If there are upcoming Mainboard IPOs closing in the next 7 days, you will receive Pushbullet notifications with the minimum fund required and details of each IPO.
    *   You'll also receive error notifications if there are any issues with the script.

## Scheduling (Optional)

You can schedule the script to run automatically at regular intervals (e.g., daily) using task schedulers:

*   **Windows:** Task Scheduler
*   **macOS:** `launchd`
*   **Linux:** `cron`

Refer to the documentation for your operating system's task scheduler for instructions on how to set up scheduled tasks.

## Customization

*   **`url` Variable:** You can modify the `url` variable in the script to scrape data from a different page on Moneycontrol if needed.
*   **`calculate_min_fund_required` Function:** If the rules for IPO fund blocking/unblocking change, or if you want to add more sophisticated logic (e.g., considering holidays), you can modify this function.
*   **Notification Format:** You can customize the format and content of the Pushbullet notifications in the `send_ipo_notifications` and `send_error_notification` functions.

## Disclaimer

*   **Website Structure Changes:** Web scraping is inherently fragile. If the structure of the Moneycontrol website changes, the scraping logic in this script might break. You may need to update the code to adapt to these changes.
*   **Terms of Service:** Always respect the website's terms of service and robots.txt file when scraping. Avoid making excessive requests in a short period, as this could lead to your IP being blocked.
*   **Data Accuracy:** The accuracy of the calculations depends on the data provided by the website. It's always a good idea to verify the information from other sources.

## Contributing

If you find any bugs or want to improve the project, feel free to open an issue or submit a pull request on GitHub.

## License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.