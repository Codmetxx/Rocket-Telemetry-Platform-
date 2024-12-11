import pyodbc
from flask import Flask ,render_template,request,redirect,url_for,session

class Login:
    def __init__(self):
        try:
            
            self.connection = pyodbc.connect(
                'DRIVER={SQL Server};' +
                'Server=DESKTOP-T5KKBFV;' +
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
            new_table="""
               DROP TABLE IF EXISTS login
               Create table login(
                id int identity(1,1) primary key,
                username varchar(50) not null,
                password varchar(50) not null,
                role varchar(20) not null
                )
            
                     """
            self.cursor.execute(new_table)
            self.connection.commit()
            print("The table is created.")
        except pyodbc.Error as ex:
            print("The process is failed.",ex)
    def insert_table(self):
        try:
            table_values = """
            INSERT INTO login (username, password, role) 
            VALUES ('admin', '12345', 'admin'), ('sencer', '12345', 'user')
            """
            
             
            self.cursor.execute(table_values)
            self.connection.commit()
            print("The values is inserted.")
        
        except pyodbc.Error as ex:
            print("The processes is failed.",ex)
    def new_user(self, username,password,role):
        try:
            check_table="Select Count(*) from login where username=?"
            self.cursor.execute(check_table,(username,))
            counter=self.cursor.fetchone()[0]
            
            if counter>0:
                return False
            
            insertion_process="""
            Insert into login(username,password,role) values(?,?,?)
            """
            self.cursor.execute(insertion_process,(username,password,role))
            self.connection.commit()
            return True 
        except pyodbc.Error as ex:
            print("Error",ex)
            return False 
    def check_email(self,email):
        try:
          if email=="123@gmail.com":
              query="Select username from login"
              self.cursor.execute(query)
              users=self.cursor.fetchall()
              registered_users=[user.username for user in users]
              session["registered_users"]=registered_users
              return registered_users
          return None 
        except pyodbc.Error as ex:
            print("Error:",ex)
            return None
    def update(self,username,new_password):
        try:
            update_query=""" 
            Update login Set password=? where username=?
            """
            self.cursor.execute(update_query,(new_password,username))
            self.connection.commit()
            return True
        except pyodbc.Error as ex:
            print("Error:",ex)
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



app = Flask(__name__, template_folder='.')
loginn= Login()
@app.route("/")
def home():
    return render_template("LoginProcedures/login.html")
@app.route("/login",methods=["POST"])
def login_interface():
    username=request.form.get("username")
    password=request.form.get("password")
    user=loginn.control_check(username,password)
    
    if user["flag"]:
        if user["role"]=="admin":
            return redirect("/admin")
        return redirect("/user")
    return render_template("LoginProcedures/login.html")
@app.route("/admin")
def admin():
    return render_template("Admin/AdminPanel.html")
@app.route("/user")
def user():
    return render_template("User/user.html")
@app.route("/new_user",methods=["GET","POST"])
def new_user():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        role=request.form.get("role")
        if loginn.new_user(username,password,role):
            return render_template("LoginProcedures/success.html")
        else:
            return render_template("LoginProcedures/new_user.html",error="The user is not added or is already exsists")
       
    return render_template("LoginProcedures/new_user.html")
@app.route("/forgot_password",methods=["GET","POST"])
def forgot_password():
    if request.method=="POST":
        email=request.form.get("email")
        users=loginn.check_email(email)
        if users:
            return redirect(url_for("new_password"))
        else:
            return render_template("LoginProcedures/forgot.html",error="The email has not found!")
    return render_template("LoginProcedures/forgot.html")
@app.route("/new_password",methods=["GET","POST"])
def new_password():
    if request.method=="POST":
        new_password=request.form.get("newPassword")
        selected_user = request.form.get("selected_user")
        registered_users=session.get("registered_users",[])
        if selec
if __name__ == "__main__":
    app.run(debug=True)

   
