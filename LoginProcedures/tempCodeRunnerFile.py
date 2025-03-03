import pyodbc
from flask import Flask ,render_template,request,redirect

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
            VALUES ('admin', '12345', 'admin'), ('sencer', '12345', 'user'), ('sencer1', '12345', 'user')
            """
            
             
            self.cursor.execute(table_values)
            self.connection.commit()
            print("The values is inserted.")
        
        except pyodbc.Error as ex:
            print("The processes is failed.",ex)
        
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
if __name__ == "__main__":
    app.run(debug=True)

   
