import pandas as pd
import datetime
import csv

add_list = ["No.", "Todo List", "Datetime", "Email_Notification"]
with open("todo-data.csv", "a", newline='', encoding='utf-8') as append_data:
    csv_writer = csv.writer(append_data)
    csv_writer.writerow(add_list)

