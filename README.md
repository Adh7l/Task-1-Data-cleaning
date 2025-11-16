Task 1 – Netflix Data Cleaning (Beginner Level)

For this task, I cleaned the Netflix Movies and TV Shows dataset. I am still learning data cleaning, so I tried to follow all the steps slowly and understand what I was doing.

The dataset had a lot of missing values in director, cast, country etc. At first I didn’t know what to do with them, but later I filled them with things like “Not Available” so it becomes more consistent. There were also some text formatting problems and too many different styles in the column names, so I changed everything to lowercase and snake_case.

The date_added column had different types of date formats, so I converted them into a proper datetime column. Some dates didn’t get converted, so they became NaT which is fine for now. The duration column was a little confusing so I split it into duration_value and duration_unit to make it simple to understand.

In the end, my cleaned dataset has 8807 rows and 15 columns, and it looks much cleaner than before. I used Spyder IDE for running my python script and generating the cleaned file.

This is my final cleaned dataset for Task 1 and I feel like I learned a lot while doing it.
