import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session
import random
import string

class Login:
    def __init__(self):
        try:
            self.connection = pyodbc.connect(
                'DRIVER={SQL Server};' +
                'Server=DESKTOP-K8LPTJ0;' +
                'Database=master;' +  
                'Trusted_Connection=True'
            )
            self.cursor = self.connection.cursor()
            print("Database connection is successful.")
            self.create_table()
            self.insert_table()
        except pyodbc.Error as ex:
            print("Database connection is failed:", ex)

    def create_table(self):
        try:
            new_table = """
               DROP TABLE IF EXISTS login
               Create table login(
                id int identity(1,1) primary key,
                username varchar(50) not null,
                password varchar(50) not null,
                email varchar(100) not null,
                role varchar(20) not null
                )
            """
            self.cursor.execute(new_table)
            self.connection.commit()
            print("The table is created.")
        except pyodbc.Error as ex:
            print("The process is failed.", ex)

    def insert_table(self):
        try:
            table_values = """
            INSERT INTO login (username, password, email, role) 
            VALUES ('admin', '12345', 'admin@example.com', 'admin'), 
                   ('sencer', '12345', '123@gmail.com', 'user')
            """
            self.cursor.execute(table_values)
            self.connection.commit()
            print("The values is inserted.")
        except pyodbc.Error as ex:
            print("The processes is failed.", ex)

    def new_user(self, username, password, email, role):
        try:
            check_table = "Select Count(*) from login where username=? OR email=?"
            self.cursor.execute(check_table, (username, email))
            counter = self.cursor.fetchone()[0]
            
            if counter > 0:
                return False
            
            insertion_process = """
            Insert into login(username, password, email, role) values(?, ?, ?, ?)
            """
            self.cursor.execute(insertion_process, (username, password, email, role))
            self.connection.commit()
            return True 
        except pyodbc.Error as ex:
            print("Error", ex)
            return False 

    def check_email(self, email):
        try:
            query = "Select username from login where email=?"
            self.cursor.execute(query, (email,))
            user = self.cursor.fetchone()
            return user is not None
        except pyodbc.Error as ex:
            print("Error:", ex)
            return False

    def update_password(self, email, new_password):
        try:
            update_query = "Update login Set password=? where email=?"
            self.cursor.execute(update_query, (new_password, email))
            self.connection.commit()
            return True
        except pyodbc.Error as ex:
            print("Error:", ex)
            return False

    def control_check(self, username, password):
        try:
            sql = "SELECT * FROM login WHERE username=? AND password=?"
            self.cursor.execute(sql, (username, password))
            user = self.cursor.fetchone()
            
            if user:
                return {
                    'flag': True,
                    'role': user.role,
                    'username': user.username
                }
            else:
                print('Login failed!')
                return {'flag': False}
                
        except pyodbc.Error as ex:
            print("Query is failed")
            return {"flag": False}

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

app = Flask(__name__, template_folder='.')
app.secret_key = 'your_secret_key_here'
loginn = Login()

@app.route("/")
def home():
    return render_template("LoginProcedures/login.html")

@app.route("/login", methods=["POST"])
def login_interface():
    username = request.form.get("username")
    password = request.form.get("password")
    user = loginn.control_check(username, password)
    
    if user["flag"]:
        if user["role"] == "admin":
            return redirect("/admin")
        return redirect("/user")
    return render_template("LoginProcedures/login.html", error="Invalid username or password")

@app.route("/admin")
def admin():
    return render_template("Admin/AdminPanel.html")

@app.route("/user")
def user():
    return render_template("User/user.html")

@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        role = request.form.get("role")
        if loginn.new_user(username, password, email, role):
            return render_template("LoginProcedures/success.html")
        else:
            return render_template("LoginProcedures/new_user.html", 
                                 error="The user is not added or username/email already exists")
    return render_template("LoginProcedures/new_user.html")

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        if loginn.check_email(email):

            verification_code = generate_verification_code()
            session['verification_code'] = verification_code
            session['reset_email'] = email
            print(f"Verification code: {verification_code}")
            return redirect(url_for('success'))
        return render_template("LoginProcedures/forgot.html", error="Email not found!")
    return render_template("LoginProcedures/forgot.html")

@app.route("/success", methods=["GET", "POST"])
def success():
    if 'verification_code' not in session:
        return redirect(url_for('forgot_password'))
        
    if request.method == "POST":
        entered_code = request.form.get("code")
        stored_code = session.get('verification_code')
        
        if entered_code == stored_code:
            session.pop('verification_code', None)
            return redirect(url_for('new_password')) 
        return render_template("LoginProcedures/success.html", error="Invalid verification code!")
    return render_template("LoginProcedures/success.html")

@app.route("/new-password", methods=["GET", "POST"])  
def new_password():                                   
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))
        
    if request.method == "POST":
        new_password = request.form.get("newPassword")
        email = session.get('reset_email')
        
        if email and loginn.update_password(email, new_password):
            session.clear()
            return redirect(url_for('home'))
        return render_template("LoginProcedures/new-password.html", 
                             error="Password update failed!")
    return render_template("LoginProcedures/new-password.html")

if __name__ == "__main__":
    app.run(debug=True)