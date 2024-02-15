from flask import Flask,render_template,jsonify
import mysql.connector
from jinja2 import Template
import requests
from jinja2 import Template
import random
from datetime import datetime, timedelta
import re
import os
current_date = datetime.now()
# API URL
api_url = 'https://hub.vong.earth/webservice/rest/server.php'
directory = '/static/reports/'
if not os.path.exists(directory):
    os.makedirs(directory)
# Access token (replace 'your-access-token' with your actual access token)
access_token = 'd478810b234eb7682244b9f474c7468f'
date_chk=False
# Function to make a request to the Moodle API
def make_moodle_api_request(function, params=None):
    data = {
        'wstoken': access_token,
        'wsfunction': function,
        'moodlewsrestformat': 'json'
    }
    if params:
        data.update(params)

    response = requests.post(api_url, data=data)
    return response.json()

# Function to generate random avatar color
def generate_random_color():
    color = '#' + ''.join(random.choices('0123456789ABCDEF', k=6))
    return color

# Course ID (replace 'course-id' with the actual course ID)
students = []
students_data=[]
course_ids = ['14', '16', '17']
for course_id in course_ids:
  # Retrieve all enrolled users
  users_response = make_moodle_api_request('core_enrol_get_enrolled_users', {
      'courseid': course_id
  })

  #  Process and collect grades for each user

  excluded_titles = ["Course total"]

  for user in users_response:
      user_id = user['id']
      fullname = user['fullname']
      email_address = user['email']

    # Retrieve grades table for the user
      grades_response = make_moodle_api_request('gradereport_user_get_grades_table', {
          'userid': user_id,
          'courseid': course_id
      })

      # Process and collect the grades for the user
      if 'tables' in grades_response and len(grades_response['tables']) > 0:
          grades_table = grades_response['tables'][0]['tabledata']
          grades_total = 0  # Initialize total grades for the user


          for grade_item in grades_table:
            if 'itemname' in grade_item and 'content' in grade_item['itemname']:
              grade_item_name = grade_item['itemname']['content']
            else:
              grade_item_name = 'N/A'
            grade = 'N/A'

            if 'grade' in grade_item:
                grade = grade_item['grade']['content']

            if 'total' in grade_item_name:
                pattern = r'\b\d{2}/\d{4}\b'

                    # Find all occurrences of the pattern in the HTML text
                matches = re.findall(pattern, grade_item_name)

                if matches:
                    title = matches[0]
                else:
                    continue


                date_format = "%m/%Y"
                date = datetime.strptime(title, date_format)
                three_months_ago = current_date - timedelta(days=60)
                date_chk=False
                if date < three_months_ago:
                    date_chk=True
            else:
                continue
            if date_chk:
                continue
            print(grade_item_name)

            # Check if the grade is numeric
            if grade.replace('.', '', 1).isdigit():
                grades_total += float(grade)

          student1 = {
              'user_id': user_id,
              'fullname': fullname,
              'email_address': email_address,
              'grades_total': grades_total,
              'avatar_color': generate_random_color()  # Generate random avatar color
          }
          students_data.append(student1)
students_dict = {}
print(students_data)
for student_data in students_data:
    user_id = student_data['user_id']
    grades_total = student_data['grades_total']

    if user_id in students_dict:
        students_dict[user_id]['grades_total'] += grades_total
    else:
        student = {
            'user_id': user_id,
            'fullname': student_data['fullname'],
            'email_address': student_data['email_address'],
            'grades_total': grades_total,
            'avatar_color': generate_random_color()
        }
        students_dict[user_id] = student


students = list(students_dict.values())
# Sort students based on grades in descending order
students.sort(key=lambda x: x['grades_total'], reverse=True)

# Retrieve top three students
top_three_students = students[:3]

students_dict = {}
for student_data in students_data:
    user_id = student_data['user_id']
    grades_total = student_data['grades_total']

    if user_id in students_dict:
        students_dict[user_id]['grades_total'] += grades_total
    else:
        student = {
            'user_id': user_id,
            'fullname': student_data['fullname'],
            'email_address': student_data['email_address'],
            'grades_total': grades_total,
            'avatar_color': generate_random_color()
        }
        students_dict[user_id] = student

students = list(students_dict.values())
# Sort students based on grades in descending order
students.sort(key=lambda x: x['grades_total'], reverse=True)

# Retrieve top three students
top_three_students = students[:3]

host = 'localhost'
user = 'vongle'
password = 'ashiv3377'
database = 'osqacademy'


try:
        # Connect to the database
        with mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        ) as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Fetch all rows from the table
                select_query = 'SELECT * FROM special_mentions_data'
                cursor.execute(select_query)
                rows = cursor.fetchall()

                # Convert the rows to a list of dictionaries
                result = [{'id': row['id'],
                           'name': row['name'],
                           'image': row['image'],
                           'title': row['title'],
                           'title_description': row['title_description'],
                           'added_at': row['added_at'].isoformat() if row['added_at'] else None
                           } for row in rows]
                result = result[::-1][:6]

except mysql.connector.Error as err:
    print("error")


html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<style>
     .main_container {
        display: flex;
        width: 100vh;
        height: 100%;
        position: absolute;
        inset: 200px 50px 50px 0;

    }

    .left {
        display: flex;
        position: relative;
    }

    .right {
        display: flex;
        position: relative;
    }

    .leaderboard {
        display: flex;
        width: 635px;
        height: 113.57px;
        left: 50px;
        top: 67px;
        position: absolute;
        background: white;
        box-shadow: 0px 0px 72.27030181884766px 3.2263529300689697px rgba(0, 0, 0, 0.25);
        border-radius: 25.81px;
        backdrop-filter: blur(59.95px);
    }

    .sub_leaderboard_rank {
        display: flex;
        width: 21.95px;
        height: 17.99px;
        left: -0px;
        top: 13.67px;
        position: relative;
        color: black;
        font-size: 15.80px;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        word-wrap: break-word
    }

    .sub_leaderboard_img {
        display: flex;
        width: 48.58px;
        height: 48.58px;
        left: 10px;
        top: 0px;
        position: relative;
        border-radius: 9999px
    }

    .sub_leaderboard_name {
        display: flex;
        left: 102.20px;
        top: 6.84px;
        position: absolute;
        color: black;
        font-size: 21.23px;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        word-wrap: break-word
    }

    .sub_leaderboard_score {
        display: flex;
        width: 52.18px;
        height: 14.75px;
        left: 391.53px;
        top: 15.47px;
        position: absolute;
        color: #A3A3A3;
        font-size: 14.39px;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        word-wrap: break-word
    }

    .sub_leaderboard_underline {
        display: flex;
        width: 417.44px;
        height: 0px;
        left: 35.99px;
        top: 63.34px;
        position: absolute;
        border-top: 0.36px rgba(94.56, 89.20, 89.20, 0.54) solid;
    }

    .sub_leaderboard_container {
        display: flex;
        width: 1440px;
        height: 967px;
        left: -49px;
        top: 450px;
        z-index: 10;
        position: absolute;
    }

    .big_red_circle {
        width: 705px;
        height: 681px;
        left: 646px;
        top: 1050px;
        position: absolute;
        background: rgba(229, 0, 0, 0.94);
        border-radius: 9999px;
    }

    .sub_leaderboard_bg {
        display: flex;
        flex-direction: column;
        gap: 40px;
        width: 544px;
        height: 653px;
        left: 0px;
        top: 412px;
        position: absolute;
        background: white;
        box-shadow: 0px 0px 90.73945617675781px rgba(0, 0, 0, 0.25);
        border-radius: 32.41px;
        backdrop-filter: blur(75.27px)
    }

    .sub_leaderboard_tab {
        display: flex;
        position: relative;
        top: 20px;
        left: 35px;
    }

    .leaderboard_container {
        width: 536px;
        height: 550.41px;
        left: 100px;
        top: 282px;
        position: absolute;
        background: white;
        box-shadow: 0px 0px 55.63670349121094px 2.483781337738037px rgba(0, 0, 0, 0.25);
        border-radius: 19.87px;
        backdrop-filter: blur(46.15px)
    }

    .special-mentions {
        width: 635px;
        height: 113.57px;
        left: 825px;
        top: 67px;
        position: absolute;
        background: white;
        box-shadow: 0px 0px 72.27030181884766px 3.2263529300689697px rgba(0, 0, 0, 0.25);
        border-radius: 25.81px;
        backdrop-filter: blur(59.95px)
    }

    .special-mentions_container {
        display: flex;
        flex-direction: column;
        gap: 75px;
        position: absolute;
        left: 851px;
        top: 350px;
    }

    .special-mentions_card {
        width: 574px;
        height: 266px;
        display: flex;
        background: white;
        box-shadow: 0px 2.2613930702209473px 42.401123046875px rgba(0, 0, 0, 0.25);
        border-radius: 28.27px;
    }

    .special-mentions_title {
        width: 303.80px;
        height: 47.53px;
        left: 225px;
        top: 49.17px;
        position: absolute;
        text-align: center;
        color: #E50000;
        font-size: 32.24px;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        word-wrap: break-word;
    }

    .special-mentions_name {
        width: 143.25px;
        height: 26.07px;
        left: 40.34px;
        top: 0px;
        position: absolute;
        text-align: center;
        color: #252525;
        font-size: 19.79px;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        word-wrap: break-word;
    }

    .special-mentions_community {
        width: 223.98px;
        height: 49.88px;
        left: 0px;
        top: 32.89px;
        position: absolute;
        text-align: center;
        color: #E50000;
        font-size: 13.57px;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        word-wrap: break-word;
    }

    .special-mentions_place {
        width: 104.18px;
        height: 16.44px;
        left: 58px;
        top: 62.89px;
        position: absolute;
        text-align: center;
        color: #26235C;
        font-size: 13px;
        font-family: 'Poppins', sans-serif;
        font-weight: 900;
        word-wrap: break-word;
    }

    .special-mentions_img {
        width: 104.18px;
        height: 105.36px;
        left: 21.44px;
        top: 29.77px;
        position: absolute;
        border-radius: 50%;
        border: 1.13px #26235C solid;
    }

    .special-mentions_border {
        width: 120.23px;
        height: 120.56px;
        left: 78.83px;
        top: 170.60px;
        border-radius: 50%;
        position: absolute;
        transform: rotate(-138.71deg);
        transform-origin: 0 0;
        border-left: 2.83px #E50000 solid;
        border-bottom: 2.83px #E50000 solid;
    }

    .nav-link {
        text-decoration: none;
        color: #E50000;
        /* Red color for links */
        font-size: 24px;
        /* Larger font size */
        font-family: 'Poppins', sans-serif;
        /* Poppins font */
        margin-right: 15px;
        /* Add spacing between links if needed */
        background-color: #ffffff;
        box-shadow: 0 2px 4px #040404;
        padding: 20px;
        border-radius: 10px;
        margin-top: 100px;

    }

    .nav-link.active {
        color: #040404;
        /* Change color for active link */
        font-weight: bolder;
        background-color: #f8f8f8;
        box-shadow: 0 2px 4px #040404;
        padding: 20px;
        border-radius: 10px;
        margin-top: 100px;
    }


    .center-heading {
        text-align: center;
        color: #E50000;
        font-size: 61.95px;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        line-height: 25.81px;
        word-wrap: break-word;
        margin-top: 50px; /* Adjust the margin as needed */
    }
    </style>
<body>
<div>
        <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
            <div class="navbar-nav">
            <a class="nav-link "  id="lifetime" onclick="changeColor('lifetime')" href="lifelong.html">Lifetime</a>
        <a class="nav-link active"  id="threemonths" onclick="changeColor('threemonths')" href="threemonth.html">3 Months</a>
        <!-- <a class="nav-link" href="house1.html" id="groupboard" onclick="changeColor('groupboard')">House</a> -->


            </div>
        </div>
    </div>
    <div class="center-heading" id="animatedHeading">ONE MONTH LEADERBOARD</div>
    <div class="main_container">

        
        <div class="left">
            <div class="big_red_circle"></div>
            <div style="width: 1710px; height: 1082px; left: -5px; top: 100px; position: absolute; overflow: hidden;">
                <!--RED BG SHAPES-->
                <div style="width: 1005.19px; height: 449.71px; left: -210.65px; top: 67.63px; position: absolute; transform: rotate(17.82deg); transform-origin: 0 0; background: #E50000; border-radius: 36px"></div>
                <div style="width: 1000px; height: 800px; right: -2142.65px; top: 387.63px; position: absolute; transform: rotate(145deg) skewX(25deg); transform-origin: 0 0; background: #E50000; border-radius: 45px"></div>
            </div>
            <!--LEADERBOARD-->
            <div>
                <div class="leaderboard" >
                        <div style="width: 567.62px; left: 33.17px; top: 44px; position: absolute; text-align: center; color: #E50000; font-size: 61.95px; font-family: 'Poppins', sans-serif;font-weight: 600; line-height: 25.81px; word-wrap: break-word">LEADERBOARD</div>
                </div>

                <div class="leaderboard_container">
                    <img style="display:flex; width: 161.10px; height: 163.74px; left: 180.46px; top: 32.82px; position: absolute; border-radius: 9999px" src="uploads/avatar.png" />
                    <div style="display:flex; left: 214.06px; top: 204.89px; position: absolute; color: black; font-size: 20.46px; font-family: 'Poppins', sans-serif;font-weight: 600; line-height: 18.41px; word-wrap: break-word">{{ top_three_students[0].fullname }} </div>
                    <div style="display:flex; width: 25.09px; height: 25.09px; left: 218.32px; top: 230px; position: absolute; color: black; font-size: 21.81px;font-family: 'Poppins', sans-serif; font-weight: 700; word-wrap: break-word">#1</div>
                    <div style="display:flex; left: 252.85px; top: 234.97px; position: absolute; color: rgba(0, 0, 0, 0.36); font-size: 19.87px; font-family: DM Sans; font-weight: 700; line-height: 18.41px; word-wrap: break-word">{{ top_three_students[0].grades_total|round(2) }} </div>

                    <img style="display:flex; width: 148.21px; height: 150.64px; left: 63.58px; top: 287.62px; position: absolute; border-radius: 9999px" src="uploads/avatar.png" />
                    <div style="display:flex; left: 90.28px; top: 445px; position: absolute; color: black; font-size: 20.46px; font-family: 'Poppins', sans-serif;font-weight: 600; line-height: 18.41px; word-wrap: break-word">{{ top_three_students[1].fullname }} </div><br>
                    <div style="display:flex; width: 30.30px; height: 24.84px; left: 90.41px; top: 467.77px; position: absolute; color: black; font-size: 21.81px;font-family: 'Poppins', sans-serif; font-weight: 700; word-wrap: break-word">#2</div>
                    <div style="display:flex; left: 129.90px; top: 472.74px; position: absolute; color: rgba(0, 0, 0, 0.36); font-size: 19.87px; font-family: DM Sans; font-weight: 700; line-height: 18.41px; word-wrap: break-word">{{ top_three_students[1].grades_total|round(2) }} </div>

                    <img style="display:flex; width: 148.21px; height: 150.64px; left: 323.39px; top: 287.62px; position: absolute; border-radius: 9999px" src="uploads/avatar.png" />
                    <div style="display:flex; left: 350.54px; top: 444.08px; position: absolute; color: black; font-size: 20.46px; font-family: 'Poppins', sans-serif;font-weight: 600; line-height: 18.41px; word-wrap: break-word">{{ top_three_students[2].fullname }} </div><br>
                    <div style="display:flex; width: 30.30px; height: 24.84px; left: 356.35px; top: 466.78px; position: absolute; color: black; font-size: 21.81px;font-family: 'Poppins', sans-serif; font-weight: 700; word-wrap: break-word">#3</div>
                    <div style="display:flex; left: 392.36px; top: 471.75px; position: absolute; color: rgba(0, 0, 0, 0.36); font-size: 19.87px; font-family: DM Sans; font-weight: 700; line-height: 18.41px; word-wrap: break-word">{{ top_three_students[2].grades_total|round(2) }} </div>
                </div>

            </div>
            <!--SUB LEADERBOARD-->
            <div class="sub_leaderboard_container">
                <div style="width: 544px; height: 653px; left: 151px; top: 111px; position: absolute">
                    <div class="sub_leaderboard_bg" >
                    {% for student in students[3:10] %}
                        <div class="sub_leaderboard_tab" >
                            <div class="sub_leaderboard_rank">#{{loop.index + 3}}</div>
                            <img class="sub_leaderboard_img" src="uploads/avatar.png" />
                            <div class="sub_leaderboard_name">{{ student.fullname }}</div>
                            <div class="sub_leaderboard_score">{{student.grades_total|round(2)}}</div>
                            <div class="sub_leaderboard_underline"></div>
                        </div>
                    {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <!-- SPECIAL MENTIONS-->
        <div class="right">
            <div class="special-mentions" >
                <div style="width: 635px; top: 44px; position: absolute; text-align: center; color: #E50000; font-size: 61.95px; font-family: 'Poppins', sans-serif;font-weight: 600; line-height: 25.81px; word-wrap: break-word">SPECIAL MENTIONS</div>
            </div>

            <div class="special-mentions_container">
            {% for mention in mentions %}
                <div class="special-mentions_card">
                    <div style="position: relative; ">
                        <div class="special-mentions_title" >{{ mention.title }}</div>
                        <div style="width: 156.46px; height: 170.60px; left: 42.09px; top: 0.17px; position: absolute">
                            <img class="special-mentions_img" src='/uploads/{{ mention.image }}' />
                            <div class="special-mentions_border"></div>
                        </div>
                        <div style="width: 319px; height: 92.77px; left: 216px; top: 106.17px; position: relative; text-align: justify; color: black; font-size: 20px; font-family: 'Poppins', sans-serif;font-weight: 500; word-wrap: break-word;margin-top: 20px; color: rgba(61, 35, 35, 0.836);">{{ mention.title_description }}<br/><br/></div>
                        <div style="width: 223.98px; height: 82.77px; left: 8px; top: 170px;  position: absolute">
                            <div class="special-mentions_name">{{ mention.name }}</div>

                        </div>
                    </div>
                </div>
            {% endfor %}

            </div>
        </div>

    </div>
    <canvas id="myCanvas" width="2000" height="800"></canvas>
    <script>
        const canvas = document.getElementById('myCanvas');
        const context = canvas.getContext('2d');

        // Set canvas width to the size of the screen
        canvas.width = window.innerWidth;

        const max_fireworks = 5,
            max_sparks = 50;
        let fireworks = [];

        for (let i = 0; i < max_fireworks; i++) {
            let firework = {
                sparks: []
            };
            for (let n = 0; n < max_sparks; n++) {
                let spark = {
                    vx: Math.random() * 5 + .5,
                    vy: Math.random() * 5 + .5,
                    weight: Math.random() * .3 + .03,
                    red: Math.floor(Math.random() * 2),
                    green: Math.floor(Math.random() * 2),
                    blue: Math.floor(Math.random() * 2)
                };
                if (Math.random() > .5) spark.vx = -spark.vx;
                if (Math.random() > .5) spark.vy = -spark.vy;
                firework.sparks.push(spark);
            }
            fireworks.push(firework);
            resetFirework(firework);
        }
        window.requestAnimationFrame(explode);

        function resetFirework(firework) {
            firework.x = Math.floor(Math.random() * canvas.width);
            firework.y = canvas.height;
            firework.age = 0;
            firework.phase = 'fly';
        }

        function explode() {
            context.clearRect(0, 0, canvas.width, canvas.height);
            fireworks.forEach((firework, index) => {
                if (firework.phase == 'explode') {
                    firework.sparks.forEach((spark) => {
                        for (let i = 0; i < 10; i++) {
                            let trailAge = firework.age + i;
                            let x = firework.x + spark.vx * trailAge;
                            let y = firework.y + spark.vy * trailAge + spark.weight * trailAge * spark.weight * trailAge;
                            let fade = i * 20 - firework.age * 2;
                            let r = Math.floor(spark.red * fade);
                            let g = Math.floor(spark.green * fade);
                            let b = Math.floor(spark.blue * fade);
                            context.beginPath();
                            context.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',1)';
                            context.rect(x, y, 4, 4);
                            context.fill();
                        }
                    });
                    firework.age++;
                    if (firework.age > 100 && Math.random() < .05) {
                        resetFirework(firework);
                    }
                } else {
                    firework.y = firework.y - 10;
                    for (let spark = 0; spark < 15; spark++) {
                        context.beginPath();
                        context.fillStyle = 'rgba(' + index * 50 + ',' + spark * 17 + ',0,1)';
                        context.rect(firework.x + Math.random() * spark - spark / 2, firework.y + spark * 4, 4, 4);
                        context.fill();
                    }
                    if (Math.random() < .001 || firework.y < 200) firework.phase = 'explode';
                }
            });
            window.requestAnimationFrame(explode);
        }

        // Resize canvas when the window is resized
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
        });
    </script>
</body>
</html>
'''
app = Flask(__name__)
template = Template(html_template)
data = {
    'top_three_students': top_three_students,
    'students': students,
    'mentions':result
}

rendered_html = template.render(data)


with open('/var/www/reports/threemonth.html', 'w') as file:
    file.write(rendered_html)

print("Leaderboard generated successfully!")
