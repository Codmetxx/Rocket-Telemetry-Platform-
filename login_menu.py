import pyodbc

class LoginInterface:
    def __init__(self):
        try:
            # Bağlantıyı oluştur
            self.connection = pyodbc.connect(
                'DRIVER={SQL Server};' +
                'Server=DESKTOP-T5KKBFV;' +
                'Database=master;' +
                'Trusted_Connection=True'
            )
            self.cursor=self.connection.cursor()
    def control_check(self,username,password):
        try:
            sql="SELECT*FROM USERS WHERE username=? AND password=?"
            self.cursor.execute(sql,(username,password))
            user=self.cursor.fetchone()
            if user:
                return{'flag':True,'role':'user.role','username':'user.username'}
            else:
                print('Login failed!')
                return {'flag':False }
            
        except pyodbc.Error as ex:
            print('Connection failed', ex)
            
  

