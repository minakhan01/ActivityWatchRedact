import eel

from redact_data import (_get_bucket_key_dict, redact_data_basic, redact_data_custom, 
	get_all_timezones, set_timezone, _load_data)

eel.init('web')

@eel.expose
def get_data_and_bucket_keys_py(json_data):
	# Copied from redact_data._load_data
    data = json_data["buckets"]
    bucket_keys = data.keys()
    # get bucket key dict
    bucket_key_dict = _get_bucket_key_dict(bucket_keys)

    return [data, bucket_key_dict]

@eel.expose
def get_timezones_py():
	all_timezones = list(get_all_timezones())
	return all_timezones

@eel.expose
def set_timezone_py(data, selected_timezone):
	return set_timezone(data, selected_timezone)

@eel.expose
def redact_data_basic_py(user_data, bucket_key_dict):
	(
		redacted_data, unique_urls, unique_app_names
	) = redact_data_basic(user_data, bucket_key_dict)

	return [redacted_data, list(unique_urls), list(unique_app_names)]

@eel.expose
def redact_data_custom_py(
	redacted_data, 
	values_to_redact, 
	unique_values, 
	unique_urls,
	unique_app_names,
	num_values_redacted
):
	url_to_redact = []
	app_to_redact = []

	for val in values_to_redact:
		if val in unique_urls:
			url_to_redact.append(val)
			unique_values.remove(val)
		elif val in unique_app_names:
			app_to_redact.append(val)
			unique_values.remove(val)

	redacted_data = redact_data_custom(
		redacted_data, url_to_redact, app_to_redact, num_values_redacted
	)

	return [redacted_data, list(unique_values)]

eel.start('index.html')