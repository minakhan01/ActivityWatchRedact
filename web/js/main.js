var basic_redact_div = document.getElementById("basic-redact-div");
var set_timezone_div = document.getElementById("set-timezone-div");
var customize_redact_div = document.getElementById("customise-redact-div");
var download_div = document.getElementById("download-div");
var datafile_input = document.getElementById("datafile-input");
var file_content_display = document.getElementById("file-content-display");
var redact_pii_button = document.getElementById("redact-pii-button");
var select_timezone = document.getElementById("select-timezone");
var set_timezone_button = document.getElementById("set-timezone");
var download_file_link = document.getElementById("download-file");
var unique_values_display = document.getElementById("values-display");
var redact_custom_button = document.getElementById("redact-custom-button");
var search_value_input = document.getElementById("search-value");
var search_button = document.getElementById("search-button");
var basic_redact_div_status = document.getElementById("basic-redact-div-status");
var set_timezone_div_status = document.getElementById("set-timezone-div-status");
var customize_redact_div_status = document.getElementById("customise-redact-div-status");
var file_upload_form_status = document.getElementById("file-upload-form-status");

var data;
var bucket_key_dict;
var redacted_data;
var unique_urls;
var unique_app_names;
var unique_values;
var values_to_redact = [];

async function add_timezone_options(){
	var all_timezones = await eel.get_timezones_py()();
	all_timezones.sort();

	for (var i = 0; i <= all_timezones.length - 1; i++) {
		var timezone_option = document.createElement("option");
		timezone_option.text = all_timezones[i];
		select_timezone.add(timezone_option);
	}
}
add_timezone_options();


function update_download_link(){
	var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(redacted_data));
	download_file_link.setAttribute("href", dataStr);
	download_file_link.setAttribute("download", "redacted_data.json");
}

function clear_unique_values_display(){
	while(unique_values_display.firstChild){
		unique_values_display.removeChild(unique_values_display.lastChild)
	}
}

function update_unique_values_display(unique_values_updated){
	for (var i = 0; i <= unique_values_updated.length -1; i++) {
		var unique_value_item = document.createElement("li");
		unique_value_item.classList.add("unique-value");
		unique_value_item.innerHTML = unique_values_updated[i];
		unique_value_item.id = unique_values_updated[i] + "-item";
		unique_value_item.name = unique_values_updated[i];

		unique_value_item.onclick = function(){
			this.classList.toggle("unique-value-selected");

			if (this.classList.contains("unique-value-selected")){
				values_to_redact.push(this.name);
			}
			else{
				while(true){
					var ind = values_to_redact.indexOf(this.name);

					if (ind == -1)
						break;

					values_to_redact.splice(ind, 1);
				}
			}
		}

		unique_values_display.appendChild(unique_value_item);
	}
}

datafile_input.onchange = function(){
	var file = datafile_input.files[0];

	var reader = new FileReader();

	reader.onloadend = async function(){
		file_upload_form_status.innerHTML = "Uploading file, please wait..."
		var dataJSON = JSON.parse(reader.result);
		var data_arr = await eel.get_data_and_bucket_keys_py(dataJSON)();

		data = data_arr[0];
		bucket_key_dict = data_arr[1];
		file_upload_form_status.innerHTML = "File upload complete."
	}

	reader.readAsText(file);
}

redact_pii_button.onclick = async function(){
	if (!((typeof data === 'undefined') || (data === null))){
		basic_redact_div_status.innerHTML = "Basic redaction in progress, please wait..."
		var redacted_data_arr = await eel.redact_data_basic_py(data, bucket_key_dict)();

		redacted_data = redacted_data_arr[0];
		unique_urls = redacted_data_arr[1];
		unique_app_names = redacted_data_arr[2];

		unique_values = unique_urls.concat(unique_app_names);
		unique_values.sort();

		update_unique_values_display(unique_values);
		basic_redact_div_status.innerHTML = "Basic redaction complete."
	}
}

set_timezone_button.onclick = async function(){
	if (!((typeof redacted_data === 'undefined') || (redacted_data === null))){
		set_timezone_div_status.innerHTML = "Setting timezone, please wait..."
		var selected_timezone = select_timezone.value
		if (!(selected_timezone === null)){
			redacted_data = await eel.set_timezone_py(redacted_data, selected_timezone)()
		}

		set_timezone_div_status.innerHTML = "Timezone set."
		update_download_link();
	}
}

redact_custom_button.onclick = async function(){
	if (!((typeof redacted_data === 'undefined') || (redacted_data === null))){
		customize_redact_div_status.innerHTML = "Custom redaction in progress, please wait..."
		var redact_custom_arr = await eel.redact_data_custom_py(redacted_data, values_to_redact, unique_values, unique_urls, unique_app_names)();
		values_to_redact = [];

		redacted_data = redact_custom_arr[0];
		unique_values = redact_custom_arr[1];

		unique_values.sort();
		clear_unique_values_display();
		update_unique_values_display(unique_values);

		update_download_link();
		customize_redact_div_status.innerHTML = "Custom redaction complete."
	}
}

search_button.onclick = function(){
	var search_value_str = search_value_input.value.toLowerCase();

	var unique_value_items = unique_values_display.childNodes;

	for (var i = 0; i <= unique_value_items.length - 1; i++) {
		var item = unique_value_items[i]

		if (item.classList.contains("unique-value")){
			if (item.name.toLowerCase().includes(search_value_str)){
				item.classList.add("unique-value-selected");
				values_to_redact.push(item.name);
			}
		}
	}
}
