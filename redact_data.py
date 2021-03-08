import scrubadub
import urllib
import json
import logging
import pytz
import nltk
nltk.download('punkt')

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

scrubber = scrubadub.Scrubber()

def _read_file(input_filepath):
    with open(input_filepath) as f:
        data = json.load(f)
    return data

def _write_file(output_filepath, data):
    with open(output_filepath, 'w') as json_file:
        json.dump(data, json_file)
    logging.info("Redacted data written to " + output_filepath)

def _get_bucket_key_dict(bucket_keys):
    bucket_key_dict = {
    'afk': None,
    'desktop': None,
    'browser': None,
    'stopwatch': None
    }

    for key in bucket_keys:

        if 'aw-watcher-afk' in key:
            bucket_key_dict['afk'] = key
        
        if 'aw-watcher-window' in key:
            bucket_key_dict['desktop'] = key
        
        if 'aw-watcher-web' in key:
            bucket_key_dict['browser'] = key
        
        if 'aw-stopwatch' in key:
            bucket_key_dict['stopwatch'] = key

    return bucket_key_dict

def _get_data_using_key(data, key):
    if key:
        return data[key]
    else:
        return None

def _load_data(json_file):

    data = _read_file(json_file)

    # assign data to child of buckets
    data = data['buckets']

    # get all buckets in data
    bucket_keys = data.keys()

    # get bucket key dict
    bucket_key_dict = _get_bucket_key_dict(bucket_keys)


    return data, bucket_key_dict

def _get_base_url(orig_url):
    url_split_result = urllib.parse.urlsplit(orig_url)
    return url_split_result.netloc

def _redact_url(url):
    base_url = _get_base_url(url)
    return base_url

def _redact_text(text):
    if text:
        redacted_text = scrubber.clean(text, replace_with='identifier')
        return redacted_text
    else:
        return text

def _redact_by_keyword(text, keyword, replacement):
    return text.replace(keyword, replacement)

def _redact_browser_events(browser_data_events):
    unique_urls = set()
    for event in browser_data_events:
        url = _redact_url(event['data']['url'])
        event['data']['url'] = url
        unique_urls.add(url)
        del event['data']['title']
    return browser_data_events, unique_urls

def _redact_desktop_events(desktop_data_events):
    unique_app_names = set()
    for event in desktop_data_events:
        #event['data']['app'] = _redact_text(event['data']['app'])
        unique_app_names.add(event['data']['app'])
        del event['data']['title']
    return desktop_data_events, unique_app_names

def redact_stopwatch_data(stopwatch_data):
    redacted_stopwatch_bucket_id = _redact_text(stopwatch_data['id'])
    redacted_stopwatch_name = _redact_text(stopwatch_data['name'])
    redacted_stopwatch_hostname = _redact_text(stopwatch_data['hostname'])

    stopwatch_data['id'] = redacted_stopwatch_bucket_id 
    stopwatch_data['name'] = redacted_stopwatch_name
    stopwatch_data['hostname'] = redacted_stopwatch_hostname

    return stopwatch_data

def redact_afk_data(afk_data):
    redacted_afk_bucket_id = _redact_text(afk_data['id'])
    redacted_afk_name = _redact_text(afk_data['name'])
    redacted_afk_hostname = _redact_text(afk_data['hostname'])

    afk_data['id'] = redacted_afk_bucket_id 
    afk_data['name'] = redacted_afk_name
    afk_data['hostname'] = redacted_afk_hostname

    return afk_data

def redact_browser_data(browser_data):
    redacted_browser_bucket_id = _redact_text(browser_data['id'])
    redacted_browser_name = _redact_text(browser_data['name'])
    redacted_browser_hostname = _redact_text(browser_data['hostname'])

    browser_data['id'] = redacted_browser_bucket_id 
    browser_data['name'] = redacted_browser_name
    browser_data['hostname'] = redacted_browser_hostname

    browser_data_events = browser_data['events']
    browser_data['events'], unique_urls = _redact_browser_events(browser_data_events)

    return browser_data, unique_urls

def redact_desktop_data(desktop_data):

    redacted_desktop_bucket_id = _redact_text(desktop_data['id'])
    redacted_desktop_name = _redact_text(desktop_data['name'])
    redacted_desktop_hostname = _redact_text(desktop_data['hostname'])

    desktop_data['id'] = redacted_desktop_bucket_id 
    desktop_data['name'] = redacted_desktop_name
    desktop_data['hostname'] = redacted_desktop_hostname

    desktop_data_events = desktop_data['events']
    desktop_data['events'], unique_app_names = _redact_desktop_events(desktop_data_events)

    return desktop_data, unique_app_names

def redact_selected_urls(web_browser_data, urls_to_remove, num_values_redacted):
    web_browser_data_events = web_browser_data['events']

    # redacted_browser_data_events = [event for event in web_browser_data_events if not event['data']['url'] in urls_to_remove]
    
    # create redaction mapping dictionary
    redaction_mapping = {
        url:'redacted_url_'+str(num_values_redacted+i) for i, url in enumerate(urls_to_remove)
    }

    redacted_browser_data_events = []
    for event in web_browser_data_events:
        if event['data']['url'] in urls_to_remove:
            event['data']['url'] = redaction_mapping[event['data']['url']]
        redacted_browser_data_events.append(event)

    web_browser_data['events'] = redacted_browser_data_events

    return web_browser_data


def redact_app_names(desktop_data, app_names_to_remove, num_values_redacted):
    desktop_data_events = desktop_data['events']

    # redacted_desktop_data_events = [event for event in desktop_data_events if not event['data']['app'] in app_names_to_remove]

    # create redaction mapping dictionary
    redaction_mapping = {
        app:'redacted_app_'+str(num_values_redacted+i) for i, app in enumerate(app_names_to_remove)
    }

    redacted_desktop_data_events = []
    for event in desktop_data_events:
        if event['data']['app'] in app_names_to_remove:
            event['data']['app'] = redaction_mapping[event['data']['app']]
        redacted_desktop_data_events.append(event)

    desktop_data['events'] = redacted_desktop_data_events

    return desktop_data

def redact_data_basic(data, bucket_key_dict):
    # Remove hostname, Rename buckets, Redact titles

    redacted_data = {
        "buckets": {
            "aw-watcher-window": None,
            "aw-watcher-afk": None,
            "aw-watcher-web": None,
            "aw-watcher-stopwatch": None
    }}

    # process afk data
    afk_data = _get_data_using_key(data, bucket_key_dict['afk'])
    redacted_data["buckets"]["aw-watcher-afk"] = redact_afk_data(afk_data)
    logging.info("AFK data successfully redacted (basic)...")
    
    # process web data
    browser_data = _get_data_using_key(data, bucket_key_dict['browser'])
    redacted_data["buckets"]["aw-watcher-web"], unique_urls = redact_browser_data(browser_data)
    logging.info("Web data successfully redacted (basic)...")

    # process window data
    desktop_data = _get_data_using_key(data, bucket_key_dict['desktop'])
    redacted_data["buckets"]["aw-watcher-window"], unique_app_names = redact_desktop_data(desktop_data)
    logging.info("Window data successfully redacted (basic)...")
    
    # process stopwatch data
    stopwatch_data = _get_data_using_key(data, bucket_key_dict['stopwatch'])
    redacted_data["buckets"]["aw-watcher-stopwatch"] = redact_stopwatch_data(stopwatch_data)
    logging.info("Stopwatch data successfully redacted (basic)...")

    return redacted_data, unique_urls, unique_app_names

def redact_data_custom(redacted_data, urls_to_remove, app_names_to_remove, num_values_redacted):
    # Remove app names, urls
    # process web data to remove selected urls
    browser_data =  redacted_data["buckets"]["aw-watcher-web"]
    redacted_data["buckets"]["aw-watcher-web"] = redact_selected_urls(browser_data, urls_to_remove, num_values_redacted)
    logging.info("Web data successfully redacted (user selected)...")

    num_values_redacted += len(urls_to_remove)

    # process window data to remove app names
    desktop_data = redacted_data["buckets"]["aw-watcher-window"]
    redacted_data["buckets"]["aw-watcher-window"] = redact_app_names(desktop_data, app_names_to_remove, num_values_redacted)
    logging.info("Window data successfully redacted (user selected)...")

    return redacted_data

def get_all_timezones():
    return pytz.all_timezones_set

def set_timezone(data, selected_timezone):
    data["timezone"] = selected_timezone
    return data

def main_test(input_file, output_file):

    data, bucket_key_dict = _load_data(input_file)
    redacted_data, unique_urls, unique_app_names = redact_data_basic(data, bucket_key_dict)

    url_blacklist = set(["docs.google.com", "www.deeplearningbook.org"])
    app_blacklist = set(["Finder"])

    user_selected_timezone = 'America/New_York'

    # Remove apps and urls from user provided black list
    redacted_data = redact_data_custom(redacted_data, url_blacklist, app_blacklist)
    
    # set user selected timezone
    redacted_data = set_timezone(redacted_data, user_selected_timezone)

    _write_file(output_file, redacted_data)

if __name__ == "__main__":
    filepath1 = "./aw-buckets-export-advait-Dec2.json"
    filepath2 = "./aw-buckets-export-sri.json"
    output_file = "./redacted-data.json"

    main_test(filepath2, output_file)