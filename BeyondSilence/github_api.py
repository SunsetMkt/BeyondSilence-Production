import logging
import time

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s",
)

from . import config_utils as Config


def get_recent_activities_of(user_name):
    query_url = f"https://api.github.com/users/{user_name}/events/public"  # Return latest 90 days activities
    req = None
    fail_count = 0
    while (
        req is None
        or req.status_code == 403
        or req.status_code == 429
        or req.status_code == 404
    ):
        req = requests.get(query_url)
        if req.status_code == 403 or req.status_code == 429:
            # Wait for rate limit to reset
            reset_time = int(req.headers.get("x-ratelimit-reset"))
            logging.info(f"Rate limit reset time: {reset_time}")
            wait_time = reset_time - time.time() + 1
            logging.info(f"Wait time: {wait_time}")
            if wait_time < 0:  # Failsafe
                wait_time = 0
            req = None  # Reset req
            time.sleep(wait_time)
        elif req.status_code == 404:
            logging.info(f"User {user_name} not found")
            if Config.config["trigger_when_api_404"]:
                logging.info(f"Trigger when API 404 is enabled")
                return []  # Activities is empty, returning 91
            else:
                logging.error(f"User {user_name} not found")
                raise Exception(f"User {user_name} not found")
        elif not req.ok:  # Request failed
            fail_count += 1
            if fail_count >= 5:  # Attempt 5 times
                logging.error(
                    f"Failed to get recent activities of {user_name}, status code: {req.status_code}, return the bad response"
                )
                break
            else:
                logging.info(
                    f"Failed to get recent activities of {user_name}, status code: {req.status_code}, retrying..."
                )
                req = None  # Reset req
                time.sleep(5)

    logging.info(f"Request status code: {req.status_code}")
    req.raise_for_status()
    logging.info(f"Request successful")
    return req.json()


def get_latest_activity_days_to_now(activities):
    # if activities is empty []
    if activities == []:
        logging.info(f"Activities is empty, returning 91")
        return 91
    latest_formatted_date = activities[0]["created_at"]  # YYYY-MM-DDTHH:MM:SSZ
    latest_date = time.strptime(latest_formatted_date, "%Y-%m-%dT%H:%M:%SZ")
    latest_timestamp = time.mktime(latest_date)
    now_timestamp = time.time()
    days = int((now_timestamp - latest_timestamp) / 86400)
    logging.info(f"Latest activity is {days} day(s) ago")
    return days


def get_days_of_inactivity(user_name):
    activities = get_recent_activities_of(user_name)
    days = get_latest_activity_days_to_now(activities)
    return days
