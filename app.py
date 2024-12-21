import pyodbc
from flask import Flask, jsonify,render_template, request, redirect, url_for, session
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
            self.create_projects_table()  
            self.create_interfacetable()  
            
        except pyodbc.Error as ex:
            print("Database connection is failed:", ex)

    def create_table(self):
        try:
            drop_rocket = """
            DROP TABLE IF EXISTS rocket_data;
          
            
            """
            drop_projects= """
            
            DROP TABLE IF EXISTS projects;
            """
            self.cursor.execute(drop_rocket)
            self.cursor.execute(drop_projects)
            new_table = """
               DROP TABLE IF EXISTS login;
               Create table login(
                id int identity(1,1) primary key,
                username varchar(50) not null UNIQUE,
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
    def create_projects_table(self):
        try:
            new_query = """
            DROP TABLE IF EXISTS projects;
            CREATE TABLE projects(
                id INT IDENTITY(1,1) PRIMARY KEY,
                username VARCHAR(50),
                project_name VARCHAR(50),
                rocket_name VARCHAR(50),
                rocket_image VARBINARY(MAX),
                payload_name VARCHAR(50),
                payload_image VARBINARY(MAX),
                country VARCHAR(50),
                city VARCHAR(50),
                district VARCHAR(50),
                timestamp DATETIME DEFAULT GETDATE(),
                FOREIGN KEY(username) REFERENCES login(username) ON DELETE CASCADE
            );
            """
            self.cursor.execute(new_query)
            self.connection.commit()
            print("projects table is created")
            return True
        except pyodbc.Error as ex:
            print("Error:", ex)
            return False
    
    def projects_insertion(self, username, project_data):
        try:
            new_query = """
            SELECT count(*) FROM projects WHERE username=?
            """
            self.cursor.execute(new_query, (username,))
            project_count = self.cursor.fetchone()[0]
            
            if project_count < 10:
                insert_newproject = """
                INSERT INTO projects(
                    username, project_name, rocket_name, rocket_image,
                    payload_name, payload_image, country, city, district
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.cursor.execute(
                    insert_newproject,
                    (
                        username,
                        project_data['project_name'],
                        project_data['rocket_name'],
                        project_data['rocket_image'],
                        project_data['payload_name'],
                        project_data['payload_image'],
                        project_data['country'],
                        project_data['city'],
                        project_data['district']
                    )
                )
                self.connection.commit()
                return True
            else:
                print("You reached the maximum project number!")
                return False
        except pyodbc.Error as ex:
            print("Error:", ex)
            return False
        
    
  
    def project_details(self,username,id):
        try:
            new_query="""
            select project_name,rover_name from projects
            where username=? and id=?
            """
            self.cursor.execute(new_query,(username,id))
            return self.cursor.fetchone()
        except pyodbc.Error as ex:
            print("Error:",ex)
            return False
            
    def delete_project(self, project_id, username):
        try:
            query = """
            DELETE FROM projects 
            WHERE id = ? AND username = ?
            """
            self.cursor.execute(query, (project_id, username))
            self.connection.commit()
            return True
        except pyodbc.Error as ex:
            print("Error:", ex)
            return False
            
    
    def create_interfacetable(self):
        try:
             rocket_table = """
             DROP TABLE IF EXISTS rocket_data;
             CREATE TABLE rocket_data(
                 
                 
                 id INT IDENTITY(1,1) PRIMARY KEY,
                 username VARCHAR(50),
                 project_id INT,
                 mission_time VARCHAR(20),
                 altitude FLOAT,
                 speed FLOAT,
                 acceleration FLOAT,
                 temprature FLOAT,
                 latitude FLOAT,
                 longitude FLOAT,
                 rocket_id VARCHAR(50),
                 timestamp DATETIME DEFAULT GETDATE(),
                 FOREIGN KEY (username) REFERENCES login(username),
                 FOREIGN KEY(project_id) REFERENCES projects(id)
                 );
                 """
                 
             self.cursor.execute(rocket_table)
             self.connection.commit()
             print("Rocket table is created.")
             return True
            
        except pyodbc.Error as ex:
            print("Erorr:",ex)
            return False
    def rocketdata_insertion(self,rocket_data):
        try:
            insert_query="""
             INSERT INTO rocket_data(
            username, project_id, mission_time, altitude, 
            speed, acceleration, temprature, latitude, 
            longitude, rocket_id)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(insert_query,(rocket_data["username"],rocket_data["project_id"],rocket_data["mission_time"],rocket_data["altitude"],rocket_data["speed"],rocket_data["acceleration"],rocket_data["temprature"],rocket_data["latitude"],rocket_data["longtitude"],rocket_data["rocket_id"]))
            self.connection.commit()
            print("the insertion succesful")
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
    username=request.form.get("username")
    password=request.form.get("password")
    user=loginn.control_check(username,password)
    
    if user["flag"]:
        session["username"]=user["username"]
        session["role"]=user["role"]
        
        if user["role"] == "admin":
            return redirect("/admin")
        return redirect("/user")
    return render_template("LoginProcedures/login.html", error="Invalid username or password")

@app.route("/admin")
def admin():
    return render_template("Admin/AdminPanel.html")

@app.route("/user")
def user():
    if "username" not in session:
        return redirect(url_for("login_interface"))
    username = session["username"]
    try:
        query = """
        SELECT id, project_name 
        FROM projects 
        WHERE username = ?
        """
        loginn.cursor.execute(query, (username,))
        projects = loginn.cursor.fetchall()
        project_list = [{"id": p[0], "name": p[1]} for p in projects]
        return render_template("user.html", username=username, projects=project_list)
    except Exception as e:
        print("Error:", e)
        return render_template("user.html", username=username, projects=[])

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

@app.route("/get_projects")
def get_projects():
    if "username" not in session:
        return jsonify([])
    username=session["username"]
    try:
        query="""
        select id,project_name from projects
        where username=?
        """        
        loginn.cursor.execute(query,(username,))
        projects=loginn.cursor.fetchall()
        project_list=[]
        for i in projects:
            project_list.append({"id":i[0],"name":i[1]})
        return jsonify(project_list)
    except Exception as ex:
        print("Erro:",ex)
        return jsonify([])

@app.route("/add_project", methods=["POST"])
def add_project():
    if "username" not in session:
        return jsonify({"flag": False, "message": "Not authorized"})
        
    try:
        username = session["username"]
        
        project_data = {
            'project_name': request.form.get('project_name'),
            'rocket_name': request.form.get('rocket_name'),
            'rocket_image': request.files['rocket_image'].read() if 'rocket_image' in request.files else None,
            'payload_name': request.form.get('payload_name'),
            'payload_image': request.files['payload_image'].read() if 'payload_image' in request.files else None,
            'country': request.form.get('country'),
            'city': request.form.get('city'),
            'district': request.form.get('district')
        }
        
        if loginn.projects_insertion(username, project_data):
            return jsonify({"flag": True, "message": "Project added successfully."})
        return jsonify({"flag": False, "message": "Failed to add project"})
        
    except Exception as e:
        print("Error:", e)
        return jsonify({"flag": False, "message": str(e)})

@app.route("/delete_project/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    if "username" not in session:
        return jsonify({"success": False, "message": "Not authorized"})
    
    username = session["username"]
    success = loginn.delete_project(project_id, username)
    
    return jsonify({"success": success})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        session.clear()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/interface", methods=["GET", "POST"])
def interface():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    username = session["username"]
    project_id = request.args.get("id")
    
    try:
        user_query = """
        SELECT id, username FROM login WHERE username = ?
        """
        project_query = """
        SELECT project_name, rocket_name FROM projects 
        WHERE id = ? AND username = ?
        """
        
        loginn.cursor.execute(user_query, (username,))
        user_data = loginn.cursor.fetchone()
        
        loginn.cursor.execute(project_query, (project_id, username))
        project_data = loginn.cursor.fetchone()
        
        if user_data and project_data:
            return render_template(
                "Interface/Interface.html",
                username=username,
                user_id=str(user_data[0]).zfill(6), 
                project_name=project_data[0],
                rocket_name=project_data[1]
            )
            
    except Exception as e:
        print("Error:", e)
        
    return redirect(url_for('user'))

if __name__ == "__main__":
    app.run(debug=True)