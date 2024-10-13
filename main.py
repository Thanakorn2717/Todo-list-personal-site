import pandas as pd
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, SelectField
from wtforms.validators import DataRequired
import csv
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

'''
Red underlines? Install the required packages first:
Open the Terminal in PyCharm (bottom left).

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
sender_email = "_ _ _"
receiver_email = "_ _ _"
password = "_ _ _"  # For Gmail, use an App Password if 2FA is enabled

data = pd.read_csv("todo-data.csv")
for label, row in data.iterrows():
    date_time = pd.to_datetime(row["Datetime"])
    notify_confirm = row["Email_Notification"]
    todo_name = row["Todo List"]
    current_date = datetime.datetime.now()
    print(todo_name)
    if (current_date >= date_time) and (notify_confirm == "Yes"):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = "Todo Notification"
            body = f" Don't forget to do this activity --> {todo_name}"
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP server
            server.starttls()  # Start TLS encryption
            server.login(sender_email, password)  # Log in to the server
            server.send_message(msg)
            print("Email sent successfully!")

            data.loc[label, 'Email_Notification'] = "Done"
            data.to_csv("todo-data.csv", index=False)
            print("Notification is updated")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            server.quit()  # Close the connection


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# Exercise:
# add: Location URL, open time, closing time, coffee rating, Wi-Fi rating, power outlet rating fields
# make coffee/Wi-Fi/power a select element with choice of 0 to 5.
# e.g. You could use emojis ☕️/💪/✘/🔌
# make all fields required except submit
# use a validator to check that the URL field has a URL entered.
# ---------------------------------------------------------------------------

class TodoForm(FlaskForm):
    todo = StringField('Todo name', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    notify_mail = SelectField('Email Notification', validators=[DataRequired()],
                              choices=[("Yes", "Yes"), ("No", "No")])
    submit = SubmitField('Submit')


class DeleteForm(FlaskForm):
    number_to_delete = StringField('No.', validators=[DataRequired()], render_kw={"class": "custom-input"})
    submit = SubmitField('Delete')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def new_todo():
    form = TodoForm()
    # Exercise:
    # Make the form write a new row into Todo-data.csv
    # with   if form.validate_on_submit()
    # add_list = ["No.", "Todo List", "Datetime", "Email_Notification"]

    if form.date.data is None:
        today = datetime.datetime.now()
        Datetime = pd.to_datetime(str(today))
    else:
        Datetime = pd.to_datetime(form.date.data + " " + form.time.data)

    df = pd.read_csv("todo-data.csv")
    try:
        last_row = df.iloc[-1]
    except IndexError:
        todo_number = 1
    else:
        todo_number = last_row["No."] + 1

    Todo = form.todo.data
    Notify = form.notify_mail.data
    add_list = [todo_number, Todo, Datetime, Notify]
    print("add list: ", add_list)
    if form.validate_on_submit():
        with open("todo-data.csv", "a", newline='', encoding='utf-8') as append_data:
            csv_writer = csv.writer(append_data)
            csv_writer.writerow(add_list)
        return redirect(url_for("todo"))

    return render_template('add.html', form=form)


@app.route('/todo', methods=["GET", "POST"])
def todo():
    form = DeleteForm()
    if form.validate_on_submit():
        delete_number = int(form.number_to_delete.data)
        df = pd.read_csv("todo-data.csv")
        if delete_number in df["No."].to_list():
            print("yes")
            df_dropped = df[df["No."] != delete_number]
            df_dropped.to_csv('todo-data.csv', index=False)
        return redirect(url_for('todo'))

    with open('todo-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('todo.html', todo=list_of_rows, form=form)


if __name__ == '__main__':
    app.run(debug=True)
