pages= [

	# Main page where services are listed
	{
		"name": "services_page", 
		"url": "/m/all-services",

		"services_links": ".mg-panel__template-item>a",
		"cookie_dismiss_button": ".cookie-dismiss-btn"
	},

	# Service page
	{
		"name": "service_page",
		"find_help_button": ".js__formEntry"
	},

	#Page where description of task is required
	{
		"name": "task_description_page",
		"form_titles": ".build-group__title",

		"task_interests": {
			"ready_to_book": "#intent_level_high",
			"sometime_soon_book": "#intent_level_medium",
			"just_browsing": "#intent_level_low",
			"icon": ".ss-clipboard-check" #Used to backtrack and refill same form when scraping a service
		},
		"continue_button": ".build-group__cta>button",
		"task_location": {
			"street_address": ".search-bar-container>input",
			"flat_number": ".ignored-error"
		},
		"task_items": {
			"both": "#assembly_item_type_both_ikea_and_non_ikea_items",
			"ikea": "#assembly_item_type_only_ikea_items",
			"non_ikea": "#assembly_item_type_non_ikea_items"
		},
		"task_size": {
			"small": ".build-input-list>li>#job_size_small",
			"medium": ".build-input-list>li>#job_size_medium",
			"large": ".build-input-list>li>#job_size_large"
		},
		"vehicle_requirements": {
			"not_needed": ".build-input-list>li>#vehicle_requirement_none",
			"require_car": ".build-input-list>li>#vehicle_requirement_car_or_truck",
			"require_van": ".build-input-list>li>#vehicle_requirement_truck"
		},
		"details": ".build-form-input-textfield"
	},

	#Page where taskers available are listed
	{
		"name": "tasker_listing_page",

		#To select different days
		"days": ".recommendations__schedule-filter-day__inner",
		"days_scroller": ".ss-caret-right",

		"choose_day_button": "#recommendations__schedule-option-choose_dates",
		"calendar_day_today": ".calendar__day--today",
		"calendar_days_available": ".calendar__day--hover:not(.calendar__day--disabled)",
		"apply_calendar_choice": ".calendar__apply--text-active>span",

		#Taskers and their details
		"tasker_results": ".recommendations__result--tasker",
		"tasker_info": {

			#Tasker details
			"name": ".recommendations__result-name",
			"price": ".recommendations__pill",
			"picture": ".recommendations__avatar__circular",
			"completed_tasks": ".recommendations__result-info>li>.ss-lnr-check-circle+span",
			"description": ".recommendations__blurb",
			"vehicles": ".ss-lnr-truck+span",

			"no_reviews": ".u-light",
			"reviews_button": ".js-link-reviews",
			"review_page_arrows": ".pagination-caret",
			"review_page_content": ".reviews-section:nth-child(2)",
			"reviews_close": ".lightbox--dismiss",
			
			#List of reviews
			"reviews": ".tasker-review",
			"current_review_page": ".current",
			"task_review_select": ".reviews__filter--select",
			"task_review_all": ".reviews__filter--select>[value='All']",
			#Review details
			"review_details": {
				"title": ".media--content>strong",
				"text": ".exterior__bottom--sm",
				"date": ".muted",
				#"rating_icon": ".tasker-review>div>div>i"
				"rating_icon": ".reviews-section--tasker-rating>li"
			}
		}
	},
]