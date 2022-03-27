import time
import serial
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow
from PyQt5.QtGui import QPixmap
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

##..........................................next available row...............................
def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)


##.....................................connect to google sheets.................................

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

sheet = client.open("Gspread Demo").sheet1  # Open the spreadhseet

next_row = next_available_row(sheet)
print(next_row)
count = int(next_row)

##..........................................welcomescreen.................................................
class welcomescreen(QDialog):
    def __init__(self):
        super(welcomescreen, self).__init__()
        loadUi("Welcome_Screen_UI.ui",self)
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)
    #create loginscreen object
    def gotologin(self):
        global login
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    #create account screen object
    def gotocreate(self):
        global create
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex()+1)

##..........................................login screen.................................................
class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("Login_Page_UI.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.Log_In.clicked.connect(self.loginfunction)
        self.back.clicked.connect(self.gotowelcomescreen)
        self.imageholder.setPixmap(QPixmap('back_button.png'))

    #go back to welcome screen
    def gotowelcomescreen(self):
        global login
        widget.removeWidget(login)

    #check for all the data entered and logs in user
    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        if len(user)==0 or len(password)==0:
            self.error.setText("Please input all fields.")
        else:
            conn = sqlite3.connect("shop_data.db")
            cur = conn.cursor()
            query = 'SELECT EXISTS (SELECT * FROM login_info WHERE username =\''+user+"\'"+'AND password =\''+password+"\'"+")"
            #query = 'SELECT password FROM login_info WHERE username =\''+user+"\'"
            cur.execute(query)
            result_pass = cur.fetchone()[0]
            if result_pass == 1:
                print("Successfully logged in.")
                #self.error.setText("Successfully logged in.")
                mainscreen = MainScreen()
                widget.addWidget(mainscreen)
                widget.setCurrentIndex(widget.currentIndex() + 1)
            else:
                self.error.setText("Invalid username or password")

##..........................................Main Screen.................................................
class MainScreen(QMainWindow):
    def __init__(self):
        super(MainScreen, self).__init__()
        loadUi("mainwindow.ui",self)
        self.tableWidget.setColumnWidth(0,180)
        self.tableWidget.setColumnWidth(1,180)
        self.tableWidget.setColumnWidth(2,85)
        self.tableWidget.setColumnWidth(3,85)
        self.tableWidget.setColumnWidth(4,150)
        self.tableWidget.setColumnWidth(5,150)
        self.tableWidget.setColumnWidth(6,150)
        self.tableWidget.setColumnWidth(7,140)
        self.loaddata()
        self.additem.clicked.connect(self.AddNewItemFucntion)
        self.withdrawitem.clicked.connect(self.WithdrawItemFucntion)

    #loaddata into table widget
    def loaddata(self):
        products =[{"Product ID":"123 345 456","Product Name":"Contactor","Box": 1, "Quantity": 100, "Mfg Date":"12/10/19", "Exp Date": "22/07/22", "GRN": 236788, "Status": "Available"},
                {"Product ID":"798 467 356","Product Name":"Relay","Box": 1, "Quantity": 100, "Mfg Date":"12/10/19", "Exp Date": "22/07/22", "GRN": 246588, "Status": "Available"},
                {"Product ID":"356 378 367","Product Name":"Motor","Box": 1, "Quantity": 100, "Mfg Date":"12/10/19", "Exp Date": "22/07/22", "GRN": 246598, "Status": "Available"}]
        row=0
        print(len(products))
        self.tableWidget.setRowCount(len(products))
        for item in products:
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(item["Product ID"]))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item["Product Name"])))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item["Box"])))
            self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item["Quantity"])))
            self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(str(item["Mfg Date"])))
            self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(str(item["Exp Date"])))
            self.tableWidget.setItem(row, 6, QtWidgets.QTableWidgetItem(str(item["GRN"])))
            self.tableWidget.setItem(row, 7, QtWidgets.QTableWidgetItem(str(item["Status"])))
            row=row+1

    #add new item to database
    def AddNewItemFucntion(self):
        global addnewitem
        addnewitem = AddNewItemScreen()
        widget.addWidget(addnewitem)
        widget.setCurrentIndex(widget.currentIndex()+1)

    #withdraw a item from database
    def WithdrawItemFucntion(self):
        global withdrawitem
        withdrawitem = WithdrawItemScreen()
        widget.addWidget(withdrawitem)
        widget.setCurrentIndex(widget.currentIndex()+1)

##..........................................add new item screen.................................................
class AddNewItemScreen(QDialog):
        def __init__(self):
            super(AddNewItemScreen, self).__init__()
            loadUi("addnewitem.ui", self)
            self.back.clicked.connect(self.gotomainscreen)
            self.imageholder.setPixmap(QPixmap('back_button.png'))
            self.scan.clicked.connect(self.scanfunction)
            self.add_data.clicked.connect(self.Enter_Data)

        # go back to welcome screen
        def gotomainscreen(self):
            global addnewitem
            widget.removeWidget(addnewitem)

        def scanfunction(self):
            '''print("in scanfunction")
            ser = serial.Serial('COM8', 9600)
            reply = ""
            data = ""
            reply = ser.readline().decode()
            data = reply
            print(data)
            self.productID.setText(data)
            time.sleep(1)
'''

        def AddNewItemFucntion(self):
            global addnewitem
            storednewitem = StoredNewItemScreen()
            widget.addWidget(storednewitem)
            widget.setCurrentIndex(widget.currentIndex() + 1)

        def Enter_Data(self):
            Product_ID = 12345  # data
            print(Product_ID)
            Product_Name = self.productname.text()
            print(Product_Name)
            Box = self.box.text()
            print(Box)
            Quantity = self.quantity.text()
            print(Quantity)
            Mfg_Date = self.mfgdate.text()
            print(Mfg_Date)
            Exp_Date = self.expdate.text()
            print(Exp_Date)
            GRN = self.grn.text()
            print(GRN)
            Status = "Available"
            if Product_ID == "" or Product_Name=="" or Box == "" or Quantity=="" or Mfg_Date=="" or Exp_Date==""or GRN=="":
                print("please input all fields")
            else:
                insertRow = [Product_ID, Product_Name, Box, Quantity, Mfg_Date, Exp_Date, GRN, Status]
                sheet.append_row(insertRow, table_range="A" + str(count))
                global addnewitem
                widget.removeWidget(addnewitem)
                '''global storednewitem
                storednewitem = StoredNewItemScreen()
                widget.addWidget(storednewitem)
                widget.setCurrentIndex(widget.currentIndex() + 1)'''



            '''#print(count)
            print("in enter_data")
            Product_ID = 12345 #data
            Product_Name = self.productname.text()
            Box = self.box.text()
            Quantity = self.quantity.text()
            Mfg_Date = self.mfgdate.text()
            Exp_Date = self.expdate.text()
            GRN = self.grn.text()
            Status = "Available"

            if len(str(Product_ID)) != 0 and len(str(Product_Name)) != 0 and len(str(Box)) != 0 and len(str(Quantity)) != 0 and len(str(Mfg_Date)) != 0 and len(str(Exp_Date)) != 0 and len(str(GRN)) != 0:
                insertRow = [Product_ID, Product_Name, Box, Quantity, Mfg_Date, Exp_Date, GRN, Status]
                sheet.append_row(insertRow, table_range="A" + str(count))
                time.sleep(2)
                count += 1
            else:
                print("in else lop")
                self.error.setText("Please fill in all inputs.")
                '''

                #self.add_data.clicked.connect(self.AddNewItemFucntion)

##..........................................add new item screen.................................................
class StoredNewItemScreen(QDialog):
        def __init__(self):
            super(StoredNewItemScreen, self).__init__()
            loadUi("StoredNewItem.ui", self)
            self.back.clicked.connect(self.gotomainscreen)
            self.imageholder.setPixmap(QPixmap('back_button.png'))

        # go back to welcome screen
        def gotomainscreen(self):
            global addnewitem
            widget.removeWidget(addnewitem)




##..........................................withdraw a item screen.................................................
class WithdrawItemScreen(QDialog):
        def __init__(self):
            super(WithdrawItemScreen, self).__init__()
            loadUi("withdrawitem.ui", self)
            self.back.clicked.connect(self.gotomainscreen)
            self.imageholder.setPixmap(QPixmap('back_button.png'))
            self.scan.clicked.connect(self.scanfunction)

        # go back to welcome screen
        def gotomainscreen(self):
            global withdrawitem
            widget.removeWidget(withdrawitem)

        def scanfunction(self):
            global data
            print("in scanfunction")
            ser = serial.Serial('COM8', 9600)
            reply = ""
            data = ""
            #if ser.in_waiting > 0:
            #   print("inside scan if")
            reply = ser.readline().decode()
            data = reply
            print(data)
            self.productID.setText(data)
            time.sleep(1)


##..........................................create new account screen.................................................
class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("CreateAcc_UI.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.back.clicked.connect(self.gotowelcomescreen)
        self.imageholder.setPixmap(QPixmap('back_button.png'))

    #go back to welcome screen
    def gotowelcomescreen(self):
        global create
        widget.removeWidget(create)

    #check all the data and registers new user in database
    def signupfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()
        if len(user)==0 or len(password)==0 or len(confirmpassword)==0:
            self.error.setText("Please fill in all inputs.")
        elif password!=confirmpassword:
            self.error.setText("Passwords do not match.")
        else:
            conn = sqlite3.connect("shop_data.db")
            cur = conn.cursor()
            user_info = [user, password]
            cur.execute('INSERT INTO login_info (username, password) VALUES (?,?)', user_info)
            conn.commit()
            conn.close()

            fillprofile = FillProfileScreen()
            widget.addWidget(fillprofile)
            widget.setCurrentIndex(widget.currentIndex()+1)

##..........................................user profile screen.................................................
class FillProfileScreen(QDialog):
    def __init__(self):
        super(FillProfileScreen, self).__init__()
        loadUi("fillprofile.ui",self)
        self.image.setPixmap(QPixmap('placeholder.png'))

#............................................main.............................................................
if __name__ == "__main__":
    app = QApplication(sys.argv)
    Login = welcomescreen()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(Login)
    widget.setFixedHeight(800)
    widget.setFixedWidth(1200)
    widget.setWindowTitle("Smart Inventory Management System")
    widget.show()
    app.exec_()