app_name = "waterpark"
app_title = "Waterpark"
app_publisher = "GreyCube Technologies"
app_description = "Customization for Waterpark"
app_email = "admin@greycube.in"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "waterpark",
# 		"logo": "/assets/waterpark/logo.png",
# 		"title": "Waterpark",
# 		"route": "/waterpark",
# 		"has_permission": "waterpark.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/waterpark/css/waterpark.css"
# app_include_js = "/assets/waterpark/js/waterpark.js"

# include js, css files in header of web template
# web_include_css = "/assets/waterpark/css/waterpark.css"
# web_include_js = "/assets/waterpark/js/waterpark.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "waterpark/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "waterpark/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "waterpark.utils.jinja_methods",
# 	"filters": "waterpark.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "waterpark.install.before_install"
# after_install = "waterpark.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "waterpark.uninstall.before_uninstall"
# after_uninstall = "waterpark.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "waterpark.utils.before_app_install"
# after_app_install = "waterpark.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "waterpark.utils.before_app_uninstall"
# after_app_uninstall = "waterpark.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "waterpark.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "waterpark.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
	"Payment Request": {
		"on_payment_authorized": "waterpark.waterpark.doctype.water_park_booking_request.water_park_booking_request.on_payment_request_authorized"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"waterpark.tasks.all"
# 	],
# 	"daily": [
# 		"waterpark.tasks.daily"
# 	],
# 	"hourly": [
# 		"waterpark.tasks.hourly"
# 	],
# 	"weekly": [
# 		"waterpark.tasks.weekly"
# 	],
# 	"monthly": [
# 		"waterpark.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "waterpark.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "waterpark.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "waterpark.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "waterpark.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["waterpark.utils.before_request"]
# after_request = ["waterpark.utils.after_request"]

# Job Events
# ----------
# before_job = ["waterpark.utils.before_job"]
# after_job = ["waterpark.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"waterpark.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

