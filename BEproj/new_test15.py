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

##..........................................next available row...................................................................
def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

##.....................................connect to google sheets..........................................................................

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

sheet = client.open("Gspread Demo").sheet1  # Open the spreadhseet

next_row = next_available_row(sheet)
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
        self.refresh.clicked.connect(self.loaddata)
        self.imageholder.setPixmap(QPixmap('Refresh.png'))
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
        self.updateitem.clicked.connect(self.UpdateItemFucntion)

    #loaddata into table widget
    def loaddata(self):
        print("in load function")
        row=0
        list_of_dicts = sheet.get_all_records()
        print(len(list_of_dicts))
        self.tableWidget.setRowCount(len(list_of_dicts))
        for item in list_of_dicts:
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item["Product ID"])))
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

    #add new item to database
    def UpdateItemFucntion(self):
        global updateitem
        updateitem = UpdateItemScreen()
        widget.addWidget(updateitem)
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
            global data
            print("in scanfunction")
            try:
                arduinoSerialData = serial.Serial('COM8', 9600)  # Create Serial port object called arduinoSerialData
                while (1 == 1):
                    self.productID.setText("")
                    if (arduinoSerialData.inWaiting() > 0):
                        reply = arduinoSerialData.readline().decode()
                        print(reply)
                        data = reply
                        try:
                            cell = sheet.find(data)
                            print("Found something at R%sC%s" % (cell.row, cell.col))
                            self.productID.setText("ID Already Exists")
                        except:
                            self.productID.setText(data)
                        break
            except:
                print("error")
                self.productID.setText("No COM Port")

        def AddNewItemFucntion(self):
            global addnewitem
            storednewitem = StoredNewItemScreen()
            widget.addWidget(storednewitem)
            widget.setCurrentIndex(widget.currentIndex() + 1)

        def Enter_Data(self):
            global data
            Product_ID = data
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
                self.errormessage.setText("please input all fields")
            else:
                insertRow = [Product_ID, Product_Name, Box, Quantity, Mfg_Date, Exp_Date, GRN, Status]
                sheet.append_row(insertRow, table_range="A" + str(count))
                self.errormessage.setText("New Item Added")
                #global addnewitem
                #widget.removeWidget(addnewitem)

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
            self.withdraw.clicked.connect(self.withdrawfunction)


        # go back to welcome screen
        def gotomainscreen(self):
            global withdrawitem
            widget.removeWidget(withdrawitem)

        def scanfunction(self):
            self.errormessage.setText("")
            global data
            print("in scanfunction")
            try:
                arduinoSerialData = serial.Serial('COM8', 9600)  # Create Serial port object called arduinoSerialData
                while (1 == 1):
                    if (arduinoSerialData.inWaiting() > 0):
                        reply = arduinoSerialData.readline().decode()
                        print(reply)
                        data = reply
                        self.productID.setText(data)
                        break
            except:
                print("error")
                self.productID.setText("No COM Port")

            #find the product ID in google sheets and display all the product details on gui
            try:
                cell = sheet.find(data)
                print("Found something at R%sC%s" % (cell.row, cell.col))
                product_name = sheet.cell(cell.row, 2).value
                box_val = sheet.cell(cell.row, 3).value
                qty_val = sheet.cell(cell.row, 4).value
                mfg_date = sheet.cell(cell.row, 5).value
                exp_date = sheet.cell(cell.row, 6).value
                GRN = sheet.cell(cell.row, 7).value
                self.productID.setText(data)
                self.productName.setText(product_name)
                self.Box.setText(box_val)
                self.Quantity.setText(qty_val)
                self.mfgDate.setText(mfg_date)
                self.expDate.setText(exp_date)
                self.GRN.setText(GRN)
            except:
                print("Not Found")
                self.productID.setText("Not Found")

        def withdrawfunction(self):
            global data
            print("withdraw F data is %s" %data)
            box_user_input = int(self.boxval.text())
            print(box_user_input)
            qty_user_input = int(self.quantityval.text())
            print(qty_user_input)
            withdraw_date = self.withdrawdate.text()
            print(withdraw_date)
            try:
                cell = sheet.find(data)
                print("Found something at R%sC%s" % (cell.row, cell.col))
                box_val = int(sheet.cell(cell.row, 3).value)
                qty_val = int(sheet.cell(cell.row, 4).value)
                print(box_val)
                print(qty_val)
                if (box_val >= box_user_input and qty_val >= qty_user_input):
                    print("Stock Available")
                    upt_box_val = (box_val - box_user_input)
                    upt_qty_val = (qty_val - qty_user_input)
                    print("Updated Box: %d Updated Quantity: %d" % (upt_box_val, upt_qty_val))
                    sheet.update_cell(cell.row, 3, upt_box_val)
                    sheet.update_cell(cell.row, 4, upt_qty_val)
                    self.errormessage.setText("Withdrawal Completed")
                else:
                    print("No stock")
                    self.errormessage.setText("No Stock")
            except:
                print("No Match Found")
                self.errormessage.setText("No Match Found")

##..........................................withdraw a item screen.................................................
class UpdateItemScreen(QDialog):
        def __init__(self):
            super(UpdateItemScreen, self).__init__()
            loadUi("updateitem.ui", self)
            self.back.clicked.connect(self.gotomainscreen)
            self.imageholder.setPixmap(QPixmap('back_button.png'))
            self.scan.clicked.connect(self.scanfunction)
            self.update.clicked.connect(self.Enter_Data)

        # go back to welcome screen
        def gotomainscreen(self):
            global updateitem
            widget.removeWidget(updateitem)

        def scanfunction(self):
            self.errormessage.setText("")
            global data
            print("in scanfunction")
            try:
                arduinoSerialData = serial.Serial('COM8', 9600)  # Create Serial port object called arduinoSerialData
                while (1 == 1):
                    if (arduinoSerialData.inWaiting() > 0):
                        reply = arduinoSerialData.readline().decode()
                        print(reply)
                        data = reply
                        self.productID.setText(data)
                        break
            except:
                print("error")
                self.productID.setText("No COM Port")

            #find the product ID in google sheets and display all the product details on gui
            try:
                cell = sheet.find(data)
                print("Found something at R%sC%s" % (cell.row, cell.col))
                product_name = sheet.cell(cell.row, 2).value
                box_val = sheet.cell(cell.row, 3).value
                qty_val = sheet.cell(cell.row, 4).value
                mfg_date = sheet.cell(cell.row, 5).value
                exp_date = sheet.cell(cell.row, 6).value
                GRN = sheet.cell(cell.row, 7).value
                self.productID.setText(data)
                self.productName.setText(product_name)
                self.Box.setText(box_val)
                self.Quantity.setText(qty_val)
                self.mfgDate.setText(mfg_date)
                self.expDate.setText(exp_date)
                self.GRN.setText(GRN)
            except:
                print("Not Found")
                self.productID.setText("Not Found")

        def Enter_Data(self):
            Product_ID = 12345  # data
            print(Product_ID)
            Product_Name = self.productname_2.text()
            print(Product_Name)
            Box = self.box_2.text()
            print(Box)
            Quantity = self.quantity_2.text()
            print(Quantity)
            Mfg_Date = self.mfgdate_2.text()
            print(Mfg_Date)
            Exp_Date = self.expdate_2.text()
            print(Exp_Date)
            GRN = self.grn_2.text()
            print(GRN)
            Status = "Available"
            if Product_ID == "" or Product_Name=="" or Box == "" or Quantity=="" or Mfg_Date=="" or Exp_Date==""or GRN=="":
                print("please input all fields")
                self.errormessage.setText("please input all fields")
            else:
                insertRow = [Product_ID, Product_Name, Box, Quantity, Mfg_Date, Exp_Date, GRN, Status]
                try:
                    cell = sheet.find(data)
                    print("Found something at R%sC%s" % (cell.row, cell.col))
                    row_count = cell.row
                    sheet.update_cell(row_count, 2, Product_Name)
                    sheet.update_cell(row_count, 3, Box)
                    sheet.update_cell(row_count, 4, Quantity)
                    sheet.update_cell(row_count, 5, Mfg_Date)
                    sheet.update_cell(row_count, 6, Exp_Date)
                    sheet.update_cell(row_count, 7, GRN)
                    sheet.update_cell(row_count, 8, Status)
                    self.errormessage.setText("Item Updated")
                except:
                    print("No Match Found")
                    self.errormessage.setText("No Match Found")

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