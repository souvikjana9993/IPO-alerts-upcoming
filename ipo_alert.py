import requests,os
from bs4 import BeautifulSoup
import pandas as pd
from pushbullet import Pushbullet
from datetime import datetime, timedelta
import warnings
from dotenv import load_dotenv
load_dotenv()
warnings.filterwarnings("ignore")


# Initialize Pushbullet
ACCESS_TOKEN = os.getenv('PUSHBULLET_ACCESS_TOKEN')

def send_error_notification(error_message):
    try:
        pb.push_note("IPO Alert Script Error", error_message)
    except Exception as e:
        print(f"Failed to send Pushbullet notification: {e}")


def scrape_ipo_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        upcoming_ipos_df = None
        mainboard_ipos_df = None

        for table in tables:
            # Check for Upcoming IPOs table
            if table.find('td', text='Upcoming'):
                upcoming_ipos_df = pd.read_html(str(table))[0]
                # Remove the first row which is not a header but helper text 
                upcoming_ipos_df = upcoming_ipos_df.iloc[1:]

            # Check for Mainboard IPOs table
            # look for td with text Mainline and it should be present in the table containing text open
            elif table.find('td', text='Open') and table.find('a', class_='IpoTabOpenClosed_web_ipoCatName__KLIr3 IpoTabOpenClosed_web_green__f6uzQ'):
                mainboard_ipos_df = pd.read_html(str(table))[0]
                # Remove the first row which is not a header but helper text
                mainboard_ipos_df = mainboard_ipos_df.iloc[1:]

        if upcoming_ipos_df is not None and mainboard_ipos_df is not None:
            # Rename the first column to 'Company Name' for clarity and consistency.
            columns = ['Company Name', 'Main_SME', 'Issue Price', 'Lot Size', 'Issue Size','Time Subscribed', 'Open Date', 'Close Date', 'Allotment Date','Listing Date']
            upcoming_ipos_df.columns = columns
            mainboard_ipos_df.columns = columns
            return {
                'upcoming_ipos': upcoming_ipos_df,
                'mainboard_ipos': mainboard_ipos_df
            }
        else:
            print("Could not find both Upcoming and Mainboard IPO tables.")    
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing HTML: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def calculate_min_fund_required(ipo_data, today, next_7_days_end):
    """
    Calculates the minimum fund required for Mainboard IPOs for the next 7 days (from today).

    Args:
        ipo_data: A dictionary containing 'upcoming_ipos' and 'mainboard_ipos' DataFrames.
        today: Datetime object representing today's date.
        next_7_days_end: Datetime object representing the end of the next 7 days.

    Returns:
        The minimum fund required for the next 7 days (float).
    """

    # Concatenate both DataFrames
    combined_ipos_df = pd.concat([ipo_data['upcoming_ipos'], ipo_data['mainboard_ipos']])

    # Filter for Mainboard IPOs only
    mainboard_ipos_df = combined_ipos_df[combined_ipos_df['Main_SME'] == 'Mainline']

    # Convert date columns to datetime objects, handling errors
    date_columns = ['Open Date', 'Close Date', 'Allotment Date', 'Listing Date']
    for col in date_columns:
        mainboard_ipos_df[col] = pd.to_datetime(mainboard_ipos_df[col], format='%d %b %y', errors='coerce')

    # Filter IPOs for next 7 days (from today)
    next_7_days_ipos = mainboard_ipos_df[
        (mainboard_ipos_df['Open Date'] >= today) &
        (mainboard_ipos_df['Open Date'] <= next_7_days_end)
    ]

    # Calculate fund required for each IPO
    next_7_days_ipos['Fund Required'] = pd.to_numeric(next_7_days_ipos['Issue Price'].str.replace('₹ ', ''), errors='coerce') * pd.to_numeric(next_7_days_ipos['Lot Size'], errors='coerce')

    # Calculate unblock date (allotment date + 1 day)
    next_7_days_ipos['Unblock Date'] = next_7_days_ipos['Allotment Date'] + timedelta(days=1)
    # Create a daily schedule of blocked funds
    daily_funds_blocked = {}
    for index, row in next_7_days_ipos.iterrows():
        open_date = row['Close Date']
        unblock_date = row['Unblock Date']
        fund_required = row['Fund Required']

        # Handle cases where unblock date is NaT
        if pd.isna(unblock_date):
            print(f"Warning: Unblock date is missing for {row['Company Name']}. Skipping this IPO.")
            continue

        current_date = open_date
        while current_date <= unblock_date:
            if current_date not in daily_funds_blocked:
                daily_funds_blocked[current_date] = 0
            daily_funds_blocked[current_date] += fund_required
            current_date += timedelta(days=1)
    # Find the max fund required
    max_fund_required = 0
    if daily_funds_blocked:
        max_fund_required = max(daily_funds_blocked.values())

    return max_fund_required,next_7_days_ipos
    
def send_ipo_notifications(next_7_days_ipos, min_fund):
    """
    Sends Pushbullet notifications for upcoming IPOs.

    Args:
        next_7_days_ipos: DataFrame of IPOs in the next 7 days.
        min_fund: The minimum fund required for these IPOs.
    """
    try:
        pb = Pushbullet(ACCESS_TOKEN)

        # Send notification for minimum fund required
        fund_title = "IPO Alert: Minimum Fund Required"
        fund_body = f"Minimum fund required for upcoming Mainboard IPOs in the next 7 days: ₹{min_fund:,.2f}"
        pb.push_note(fund_title, fund_body)

        # Send notifications for individual IPOs
        for index, row in next_7_days_ipos.iterrows():
            title = f"IPO Alert: {row['Company Name']}"
            body = (f"Open Date: {row['Open Date'].strftime('%Y-%m-%d')}\n"
                    f"Close Date: {row['Close Date'].strftime('%Y-%m-%d')}\n"
                    f"Issue Price: {row['Issue Price']}\n"
                    f"Lot Size: {row['Lot Size']}\n"
                    f"Issue Size: {row['Issue Size']}\n"
                    f"Main/SME: {row['Main_SME']}")
            pb.push_note(title, body)

    except Exception as e:
        error_message = f"Error sending Pushbullet notifications: {e}"
        print(error_message)
        send_error_notification(error_message)

def send_error_notification(error_message):
    """
    Sends an error notification via Pushbullet.

    Args:
        error_message: The error message to send.
    """
    try:
        pb = Pushbullet(ACCESS_TOKEN)
        pb.push_note("IPO Alert Script Error", error_message)
    except Exception as e:
        print(f"Failed to send Pushbullet error notification: {e}")


if __name__ == "__main__":
    # Example usage:
    url = "https://www.moneycontrol.com/ipo/open-upcoming-ipos/"

    try:
        ipo_data = scrape_ipo_data(url)

        if ipo_data:
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            next_7_days_end = today + timedelta(days=6)

            min_fund, next_7_days_ipos = calculate_min_fund_required(ipo_data, today, next_7_days_end)

            send_ipo_notifications(next_7_days_ipos, min_fund)

            print("IPO notifications sent (if any).")
        else:
            print("Could not retrieve IPO data.")

    except Exception as e:
        error_message = f"An unexpected error occurred in the main script: {e}"
        print(error_message)
        send_error_notification(error_message)