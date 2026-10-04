# ImadFit

#### Video Demo: https://youtu.be/yOpuSJZgJRU

#### Description:

ImadFit is a web-based bodybuilding workout tracking application designed to help users find exercises and record their workouts. The project was created as my final project for CS50x and was built using Python, Flask, SQLite, HTML, CSS, and Bootstrap.

The main purpose of ImadFit is to combine an exercise library with a personal workout tracker. Instead of needing separate websites or applications to learn how to perform an exercise and then record the workout, the user can do both within the same application.

#### User Accounts

Users can create an account with a username and password. Passwords are not stored directly in the database. Instead, they are hashed using Werkzeug's password-hashing functionality before being stored. After logging in, Flask sessions are used to keep track of the currently authenticated user.

Users can also log out of their account. Workout information is associated with the logged-in user so that users can access their own workouts.

#### Exercise Library

ImadFit includes an exercise library containing bodybuilding exercises. Each exercise has an ID, name, the muscles involved, and a YouTube video link demonstrating how the exercise can be performed.

Exercises can be searched by name, allowing users to quickly find a particular exercise. When an exercise is selected, the user can view its information and access the corresponding YouTube tutorial.

I decided to store links to YouTube videos rather than downloading the videos into the project. This keeps the application much smaller and allows YouTube to handle the video hosting.

Exercises can be added through the administrative functionality of the website, allowing the exercise library to be expanded without modifying the source code.

#### Workout Tracking

The second major part of ImadFit is the workout tracker. Users can create a workout by specifying information such as the date and workout type, for example Push or Pull.

Within a workout, users can add exercises and record the details of each set. For every set, the user can enter the number of repetitions and the weight used.

For example, a workout could contain:

* Bench Press — 10 repetitions at 60 kg
* Bench Press — 8 repetitions at 65 kg
* Shoulder Press — 10 repetitions at 20 kg

The workout and its sets are stored in the SQLite database, allowing the information to remain available after the page is refreshed.

Users can also delete individual sets if they make a mistake, and they can delete an entire workout when it is no longer needed.

#### Database

SQLite is used as the database for the application. The database stores information about users, exercises, workouts, and workout sets.

The main relationships allow a user to have multiple workouts, a workout to contain multiple sets, and each set to be associated with an exercise. This allows the application to keep track of which exercises were performed, the repetitions, and the weight used.

#### Files

`app.py` contains the main Flask application. It handles the application's routes, user authentication, database operations, exercise searching, workout creation, and workout management.

`templates/` contains the HTML templates used by the application. These templates include the pages for registration, login, exercises, workouts, and the individual exercise and workout pages.

`static/` contains static files used by the website, including CSS and other frontend resources.

`database.db` is the SQLite database containing the application's stored data.

#### Design Choices

I chose Flask because it provided a simple way to connect the website's frontend with Python and SQLite while allowing me to focus on learning how the different parts of a web application communicate with each other.

I chose SQLite because it is lightweight, easy to set up, and well suited to the size and purpose of this project. It also allowed me to practice SQL operations such as inserting, selecting, updating, and deleting data.

Bootstrap was used for parts of the interface to make the website more consistent and responsive without having to create every UI component from scratch.

For exercise tutorials, I chose to store YouTube URLs rather than video files. Downloading and storing the videos would unnecessarily increase the size of the application, while linking to YouTube provides the same basic functionality without requiring the application to host the video files.

#### How to Run

The application requires Python and Flask.

From the project directory, install the required dependencies if necessary and run:

```bash
flask run
```

The application can then be accessed through the local address provided by Flask.

The SQLite database is included with the project, so the application can use the existing database when it is started.

#### Conclusion

ImadFit was created to practice building a complete web application using the concepts learned throughout CS50x. The project combines user authentication, database management, searching, CRUD operations, and a user interface into one application.

Building ImadFit also gave me practical experience with connecting Flask routes to SQLite, managing relationships between database tables, handling user sessions, and designing a website around a real use case.
