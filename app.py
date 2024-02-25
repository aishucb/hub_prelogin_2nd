from flask import Flask, render_template, request, redirect, url_for,make_response
import requests
import mysql.connector
import random
import os
import re
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')  # Use an absolute path
mysql_db_config = {
    'host': '127.0.0.1',
    'user': 'vongle',
    'password': 'ashiv3377',
    'database': 'osqacademy',
}
# Ensure the 'uploads' folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
@app.route('/')
def hello_world():
    mysql_db_config = {
    'host': '127.0.0.1',
    'user': 'vongle',
    'password': 'ashiv3377',
    'database': 'osqacademy',
}
    try:
        mysql_connection = mysql.connector.connect(**mysql_db_config)
        if mysql_connection.is_connected():
            cursor = mysql_connection.cursor()
            query = "SELECT name, description, timestart FROM mdl_event WHERE description LIKE '%<img%' ORDER BY timestart DESC LIMIT 4;"

            cursor.execute(query)
            last_four_records = cursor.fetchall()
            total_records = len(last_four_records)
            select_query = 'SELECT * FROM special_mentions_data' 
            cursor.execute(select_query)
            rows = cursor.fetchall()
            result = [{'id': row[0],
           'name': row[1],
           'image': row[2],
           'title': row[3],
           'title_description': row[4],
           'added_at': row[5].isoformat() if row[5] else None
           } for row in rows]


            starting_row_number = max(1, total_records - 3)  # Display the last 4 rows as 96, 97, 98, 99

# Create lists as before
            names = [record[0] for record in last_four_records]
            descriptions = [record[1] for record in last_four_records]
            timestarts = [record[2] for record in last_four_records]
            for i in range(len(timestarts)):
                timestarts[i] = convert_utc_to_ist_datetime(timestarts[i])
# Create a list of row numbers
            row_numbers = list(range(starting_row_number, starting_row_number + total_records))
            img_variable_list=[]
            for i, description in enumerate(descriptions):
                res = description.split('@@PLUGINFILE@@/', 1)
                splitString = res[1]
                quote_position = splitString.find('"')
                splitString = splitString[:quote_position]
                query=f"SELECT itemid FROM mdl_files WHERE filename = '{splitString}' LIMIT 1 OFFSET 1;"
                print(query)
                cursor.execute(query)
                ids = cursor.fetchone()
                id = ids[0] if ids else None
                
                description = description.replace('@@PLUGINFILE@@', f'https://hub.vong.earth/pluginfile.php/2/calendar/event_description/{id}')
                img_start_index = description.find('<img')

                if img_start_index != -1:
       
                    img_end_index = description.find('>', img_start_index)

                    if img_end_index != -1:
            # Extract content between <img> and </img>
                        img_content = description[img_start_index :img_end_index+1]
                    else:
            # If </img> is not present, extract content until the end of the string
                        img_content = description[img_start_index :]
                    img_variable = img_content.strip()
                    img_variable_list.append(img_variable)
                descriptions[i] = remove_html_tags(description.replace(img_variable, ''))
            data_for_template = zip(row_numbers, names, descriptions, timestarts,img_variable_list)
        
            return render_template('index.html', data=data_for_template)
            
    except Exception as e:
        # Handle exceptions appropriately (e.g., log the error)
        print(f"Error: {e}")
        return render_template('error.html', error_message=str(e)), 500

    finally:
        if mysql_connection.is_connected():
            cursor.close()
            mysql_connection.close()


def convert_utc_to_ist_datetime(timestamp_utc):
    utc_datetime = datetime.utcfromtimestamp(timestamp_utc)
    utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    ist_datetime = utc_datetime.astimezone(timezone(timedelta(hours=5, minutes=30)))
    converted_ist_timestamp = ist_datetime.strftime('%Y-%m-%d %H:%M')
    return converted_ist_timestamp

def remove_html_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text()
    return text_content
from flask import send_from_directory



@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/admin')
def admin():
    return render_template('adminform.html')

@app.route('/submit_admin', methods=['POST'])
def submit():
    host = 'localhost'
    user = 'vongle'
    password = 'ashiv3377'
    database = 'osqacademy'

    try:
        if request.method == 'POST':
            name = request.form['name']
            title = request.form['title']
            description = request.form['description']

            # Use request.files to get the uploaded file
            image = request.files['image']
            
            # Save the uploaded file to the 'uploads' folder
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))

            with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            ) as conn:
                with conn.cursor(dictionary=True) as cursor:
                    # Use parameterized query to prevent SQL injection
                    insert_query = "INSERT INTO special_mentions_data (name, image, title, title_description) VALUES (%s, %s, %s, %s);"
                    cursor.execute(insert_query, (name, image.filename, title, description))

                # Commit the changes after the inner cursor block
                conn.commit()

            return "Data submitted successfully."

    except mysql.connector.Error as err:
        return f"Error: {err}"

@app.route('/awerness_admin')
def awerness_admin():
    try:
        # Establish MySQL connection
        mysql_db_config = {
            'host': '127.0.0.1',
            'user': 'vongle',
            'password': 'ashiv3377',
            'database': 'osqacademy',
        }
        mysql_connection = mysql.connector.connect(**mysql_db_config)

        if mysql_connection.is_connected():
            cursor = mysql_connection.cursor()

            # Fetch data from the 'awerness' table
            query = "SELECT id, category_id, grade, description, due_date FROM awerness;"
            cursor.execute(query)
            awerness_data = cursor.fetchall()
            

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        awerness_data = []

    finally:
        # Close the cursor and connection
        cursor.close()
        mysql_connection.close()

    return render_template('awerness.html', awerness_data=awerness_data)

@app.route('/awerness_details/<int:awerness_id>')
def awerness_details(awerness_id):
    try:
        # Establish MySQL connection
        mysql_connection = mysql.connector.connect(**mysql_db_config)

        if mysql_connection.is_connected():
            cursor = mysql_connection.cursor()

            # Fetch detailed data for a specific 'awerness_id'
            query = f"SELECT * FROM user_awerness_submission WHERE assignment_id = {awerness_id};"
            cursor.execute(query)
            awerness_details = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        awerness_details = []

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'mysql_connection' in locals() and mysql_connection.is_connected():
            mysql_connection.close()

    return render_template('awerness_details.html', awerness_details=awerness_details)

@app.route('/update_mark/<int:awerness_id>', methods=['POST'])
def update_mark(awerness_id):
    try:
        # Establish MySQL connection
        mysql_connection = mysql.connector.connect(**mysql_db_config)

        if mysql_connection.is_connected():
            cursor = mysql_connection.cursor()

            # Update the mark based on the form submission
            new_mark = request.form.get('new_mark')
            print(f"Awerness ID: {awerness_id}, New Mark: {new_mark}")  # Add this line for debugging
            print(new_mark)
            update_query = f"UPDATE user_awerness_submission SET mark = {new_mark} WHERE submission_id = {awerness_id};"
            print(f"Update Query: {update_query}")  # Add this line for debugging

            cursor.execute(update_query)
            mysql_connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'mysql_connection' in locals() and mysql_connection.is_connected():
            mysql_connection.close()

    # Return an empty response (HTTP 204 No Content)
    return make_response("", 204)



def get_grade_categories():
    connection = mysql.connector.connect(**mysql_db_config)
    cursor = connection.cursor()

    try:
        cursor.execute("select id,fullname from mdl_course;")
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err:
        print(f"Error fetching grade categories: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

# Fetch data from mdl_grade_items based on category id
def get_grade_items(category_id):
    connection = mysql.connector.connect(**mysql_db_config)
    cursor = connection.cursor()

    try:
        cursor.execute("select id,courseid,fullname from mdl_grade_categories WHERE courseid = %s;", (category_id,))
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err:
        print(f"Error fetching grade items: {err}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_category_name(category_id):
    connection = mysql.connector.connect(**mysql_db_config)
    cursor = connection.cursor()

    try:
        cursor.execute("select fullname from mdl_course WHERE id = %s;", (category_id,))
        category_name = cursor.fetchone()
        return category_name[0] if category_name else None
    except mysql.connector.Error as err:
        print(f"Error fetching category name: {err}")
        return None
    finally:
        cursor.close()
        connection.close()



@app.route('/add_awerness', methods=['GET', 'POST'])
def add_awerness():
    if request.method == 'POST':
        selected_category_id = request.form.get('category_id')
        items = get_grade_items(selected_category_id)
        return render_template('awerness_add.html', categories=get_grade_categories(), selected_category_id=selected_category_id, items=items)

    categories = get_grade_categories()
    return render_template('awerness_add.html', categories=categories)


@app.route('/get_grade_items', methods=['POST'])
def get_items():
    selected_category_id = request.form.get('category_id')
    selected_category_name = get_category_name(selected_category_id)  # Fetch the category name
    items = get_grade_items(selected_category_id)
    return render_template('awerness_add.html', category_id=selected_category_id, category_name=selected_category_name, items=items)




@app.route('/submit_admin_awerness', methods=['POST'])
def submit_admin_awerness():
    if request.method == 'POST':
        course_id = request.form.get('category_id')
        category_id = request.form.get('grade')  # Assuming the second dropdown has the name 'grade'
        description = request.form.get('description')
        due_date = request.form.get('due_date')

        try:
            # Establish MySQL connection
            mysql_db_config = {
                'host': '127.0.0.1',
                'user': 'vongle',
                'password': 'ashiv3377',
                'database': 'osqacademy',
            }
            mysql_connection = mysql.connector.connect(**mysql_db_config)

            if mysql_connection.is_connected():
                cursor = mysql_connection.cursor()

                # Execute the INSERT query
                insert_query = """
                    INSERT INTO awerness (category_id, grade, description, due_date)
VALUES (%s, %s, %s, %s);

                """
                cursor.execute(insert_query, (course_id, category_id,description,due_date))

                # Commit the changes
                mysql_connection.commit()

                print("Data successfully inserted into mdl_grade_categories table.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            # Close the cursor and connection
            cursor.close()
            mysql_connection.close()

    return redirect(url_for('/awerness_admin'))


#user panel for awerness


@app.route('/awerness_user')
def awerness_user():
    try:
        # Establish MySQL connection
        mysql_db_config = {
            'host': '127.0.0.1',
            'user': 'vongle',
            'password': 'ashiv3377',
            'database': 'osqacademy',
        }
        mysql_connection = mysql.connector.connect(**mysql_db_config)

        if mysql_connection.is_connected():
            cursor = mysql_connection.cursor()

            # Fetch data from the 'awerness' table
            query = "SELECT id, category_id, grade, description, due_date FROM awerness;"
            cursor.execute(query)
            awerness_data = cursor.fetchall()
            awerness_data = awerness_data.reverse()


    except mysql.connector.Error as err:
        print(f"Error: {err}")
        awerness_data = []

    finally:
        # Close the cursor and connection
        cursor.close()
        mysql_connection.close()

    return render_template('awerness_user.html', awerness_data=awerness_data)

@app.route('/awerness_details_user/<int:awerness_id>')
def awerness_details_user(awerness_id):
    try:
        # Establish MySQL connection
        mysql_connection = mysql.connector.connect(**mysql_db_config)

        if mysql_connection.is_connected():
            cursor = mysql_connection.cursor()

            # Fetch detailed data for a specific 'awerness_id'
            query = f"SELECT * FROM awerness WHERE id = {awerness_id};"
            cursor.execute(query)
            awerness_details = cursor.fetchone()
            query = f"SELECT id,firstname FROM mdl_user where department='vongster';"
            cursor.execute(query)
            users=cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        awerness_details = []

    finally:
        # Close the cursor and connection
        cursor.close()
        mysql_connection.close()

    return render_template('awerness_details_user.html', awerness_details=awerness_details,users=users)


@app.route('/submit_form_awerness_user', methods=['POST'])
def submit_form_awerness_user():
    if request.method == 'POST':
        assignment_id = request.form.get('id')
        course_id = request.form.get('course_id')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        user_id = request.form.get('userid')
        image = request.files.get('image')
        text = request.form.get('text')
        editable = 'editable' in request.form

        try:
            mysql_connection = mysql.connector.connect(**mysql_db_config)

            if mysql_connection.is_connected():
                cursor = mysql_connection.cursor()

                # Save the image to the 'uploads' folder
                image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)

                # Insert data into the SQL table 'user_awerness_submission'
                insert_query = """
                    INSERT INTO user_awerness_submission (assignment_id, course_id, category_id, description, due_date, user_id, image_filename, text, editable)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (assignment_id, course_id, category_id, description, due_date, user_id, image_filename, text, editable))

                mysql_connection.commit()

                print("Data successfully inserted into user_awerness_submission table.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return render_template('error.html', error_message=str(err)), 500
        finally:
            # Close the cursor and connection
            cursor.close()
            mysql_connection.close()

        return redirect(url_for('awerness_user'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


