# mealswap
A web app for meal tracking, suggestion, replacement
# Prerequisites
See [requirements.txt](https://github.com/wiktor-jedski/mealswap/blob/main/requirements.txt)
# Installation
* Clone the project
* Set up your '.env' file. You can omit 'MAIL_DEFAULT_SENDER, MAIL_USERNAME, MAIL_PASSWORD' if you are not going to create new users (or if you will create them via Click commands).
* After downloading the project, you want to create a new database. Use command 'flask create' in the command line in '/path/to/mealswap/mealswap' directory. Otherwise, you can use provided database, using 'SECRET_KEY=PLACEHOLDER' and 'SECURITY_PASSWORD_SALT=PLACEHOLDER' in your '.env' file and copying it to '/path/to/mealswap/mealswap' directory.
* Use 'autoapp.py' to start the app
# License
MIT License - see [LICENSE](https://github.com/wiktor-jedski/mealswap/blob/main/LICENSE)
