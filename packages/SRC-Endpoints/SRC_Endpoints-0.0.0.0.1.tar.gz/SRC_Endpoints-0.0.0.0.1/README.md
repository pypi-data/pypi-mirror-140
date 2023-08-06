# Forecast Flows API

This package is designed as a high level of abstraction around the API endpoints associated with Samson Rock Capital's APIs.

The package provides a lightweight, clean method for interacting with the Microservices.


## User Endpoints

- create user - ```create_user``` endpoint enables user creation.
  ```python
  create_user("username", "password")
  ```
- login user - ```login_user``` endpoint enables user login.
  ```python
  access_token = login_user("username", "password")
  ```
- get user identification - ```get_user_identification``` endpoint enables authenticated users to see who else is registered.
  ```python
  metadata = get_user_identification(12, access_token)
  ```
## Forecast Flows Endpoints

- post flows to database - ```post_flows_to_database``` endpoint enables addition of data to database.

- get all index data from database - ```get_all_index_data_from_db``` endpoint enables extraction of all index data.
  ```python
  get_all_index_data_from_db("index_name", "access_token")
  ```
- get all index review data from database - ```get_index_review_data_from_db``` endpoint enables extraction of all index data for a given review.
  ```python
  get_index_review_data_from_db("index_name", 2022, 3, "review_type", "access_token")
  ```
- get all index review data for a single day - ```get_index_review_data_single_day``` endpoint enables extraction of all index data for a given review, on a single day.
  ```python
  get_index_review_data_single_day("index_name", 2022, 3, "review_type", "2022-02-02", "access_token")
  ```
- get all index review data for a date range - ```get_index_review_data_daterange``` endpoint enables extraction of all index data for a given review, in a date range.
  ```python
  get_index_review_data_daterange("index_name", 2022, 3, "review_type", "2022-02-02", "2022-02-03" "access_token")
  ```
## Announcement Endpoints

- post announcement to database - ```post_announcements_to_database``` endpoint enables addition of data to announcement database.
- get all announcements from database - ```get_all_index_announcements_from_db``` endpoint enables collection of all announcement data.
  ```python
  get_all_index_announcements("index", "access_token")
  ```
- get multiple announcements from database - ```get_multiple_index_announcement_data_from_db``` endpoint collects multiple announcements from database. 
  ```python
  get_multiple_index_announcement_data_from_db("index", "review_type", "access_token")
  ```
- get a singular index announcement from database - ```get_index_announcement_data_from_db``` endpoint collects a singular announcement from the database.
  ```python
  get_index_announcement_data_from_db("index", 2022, 3, "review_type", "access_token")
  ```
- 

## Date Handling Endpoints

- post dates to database - ```post_dates_to_database``` endpoint enables addition of date data to the database.
- get index dates from database - ```get_index_dates_data_from_db``` endpoint enables extraction of index dates.
  ```python
  get_index_dates_data_from_db("index", 2022, 3, "review_type", "access_token")
  ```


- get all index dates from database - ```get_all_index_dates_from_db``` endpoint enables extraction of dates for a singular index.
  ```python
  get_all_index_dates_from_db("index", "access_token")
  ```
