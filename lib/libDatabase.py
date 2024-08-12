''' -------------------------------------------------------------------------------------------------
  Title:          lib DataBase

  Description:    This Script creates the Basis of the Data Storage Handling
                   It offers functionalities for the SQLite-DataBase
                   See   https://www.youtube.com/watch?v=FrTQSPSbVC0

  Author:         KauSte 
  State:          in Develop
  Version:        1.0
 -------------------------------------------------------------------------------------------------
'''
import sqlite3, os
import datetime


PathRelative = os.path.dirname(os.path.realpath(__file__))
PathDB = PathRelative + "\\database.db"



class HandleDB:
    def __init__(self, Database):       
        self.connection   = None     
        self.cursor       = None  

        self.__createTables() 

    def __del__(self):
        self.disconnectDB()
        print("Disconnect DB Object. Goodbye!")

    # -------------------------------------------------
    #   PRIVATE METHODS
    # -------------------------------------------------
    # Create Tables  
    def __createTables(self):  

        self.__createUserData()     
        self.__createWeek()     
        self.__createDay()        
        self.__createTask() 
        self.__addUser()      
    
    def __createTask(self):
        # DAYS_ID has to match with the unique ID from the Days Table
        query = """
                CREATE TABLE IF NOT EXISTS Tasks (
                ID       INTEGER     PRIMARY KEY   AUTOINCREMENT,
                Start    DATE        NOT NULL, 
                End      DATE        NOT NULL, 
                wTime    REAL        NOT NULL,
                Comment  TEXT,
                Project  TEXT,
                DAYS_ID  INTEGER     NOT NULL,
                FOREIGN KEY(DAYS_ID) REFERENCES Days(ID)
                );"""
        if (self.connectDB() == 1):
            self.connection.execute("PRAGMA foreign_keys = ON") 
            self.cursor.execute(query)
            self.disconnectDB()
        else:
            print('Failed to Create the Task Entry')
        
        
        print('Tasks-Table created')
    
    def __createDay(self):
        query = """
                CREATE TABLE IF NOT EXISTS Days (
                ID        INTEGER        PRIMARY KEY   AUTOINCREMENT,
                Date      INTEGER        NOT NULL,
                Start     TIMESTAMP      NOT NULL, 
                End       TIMESTAMP      NOT NULL, 
                wTime     REAL           NOT NULL,
                WEEKS_ID  INTEGER        NOT NULL,
                FOREIGN KEY(WEEKS_ID)    REFERENCES Weeks(ID)                  
                );"""
        if (self.connectDB() == 1):
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute(query)
            self.disconnectDB()
        else:
            print('Failed to Create the Day Entry')
        
        print('Days-Table created')

    def __createWeek(self):
        query = """
                CREATE TABLE IF NOT EXISTS Weeks (
                ID           INTEGER   PRIMARY KEY,
                Week         INTEGER   NOT NULL,
                wTime        REAL      NOT NULL, 
                PrReportTime REAL      NOT NULL                                  
                );"""
        if (self.connectDB() == 1):
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute(query)
            self.disconnectDB()
        else:
            print('Failed to Create the Week Entry')

        print('Week-Table created')

    def __createUserData(self):
        query = """
                CREATE TABLE IF NOT EXISTS UserData (
                ID        INTEGER        PRIMARY KEY   AUTOINCREMENT,
                SAPUser      TEXT  NOT NULL,
                SAPPW        TEXT  NOT NULL, 
                PrReportUser TEXT  NOT NULL,
                PrReportPW   TEXT  NOT NULL                              
                );"""
        if (self.connectDB() == 1):
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.cursor.execute(query)
            self.disconnectDB()
        else:
            print('Failed to Create the User Data Entry')

        print('User Data created')

    def __addUser(self):
        '''
        return:   INT,  -1 Failed, 1 added/updated, 0 exists
        '''
        if (self.connectDB() != 1):
            return -1
        
        # Check if ID is existing  
        cursor = self.connection.execute( f'SELECT * from UserData')   
        
        if self.getlength(cursor) == 0:
             try: 
                query = "INSERT INTO UserData (SAPUser, SAPPW, PrReportUser, PrReportPW) VALUES (?,?,?,?)"
                data  = ('MAX', '0000', 'MUSTERMANN' , '0000')   
                self.connection.execute(query, data)
                self.connection.commit()  
                self.disconnectDB()
                return 1
             
             except self.connection.Error as error:
                print("Failed to add User to Users-Table", error)
                self.disconnectDB()
                return -1

        else:
            self.disconnectDB()
            return 0
        
    # -------------------------------------------------
    #   PUBLIC METHODS
    # -------------------------------------------------
    def connectDB(self):
        try:
            self.connection = sqlite3.connect(PathDB)
            self.cursor     = self.connection.cursor()              
            return 1 
        
        except self.connection.Error as error:
            print("Failed to Connect Database", error)
            self.disconnectDB()
            return -1   
            
    def disconnectDB(self):
        if self.connection:
            self.connection.close()

    def getlength(self, cursor):
        return sum([1 for item in cursor])   

    def getWeekID(self, year, week):
        return year*100 + week  # Format 20YYWW  

    def getDateSplit(self,date):
        # Splits datetime  
        year  = date.isocalendar()[0]
        week  = date.isocalendar()[1]
        day   = int(date.strftime('%j'))
        return year,week,day
  

    # Add Table Entries   

    def addWeek(self, Year, Week, wTime=0.0, PrTime=0.0):
        '''
        return:   INT,  -1 Failed, 1 added/updated, 0 exists
        '''

        ID = self.getWeekID(Year,Week)           
        
        if (self.connectDB() != 1):
            return -1, ID
        
        # Check if ID is existing  
        cursor = self.connection.execute( f'SELECT * from Weeks where ID = {ID}')   

        if self.getlength(cursor) == 0:
            try: 
                query = f'INSERT INTO Weeks (ID, Week, wTime, PrReportTime) VALUES ({ID},{Week},{wTime},{PrTime})'   
                self.connection.execute(query)
                self.connection.commit()  
                self.disconnectDB()
                return 1, ID
            
            except self.connection.Error as error:
                print("Failed to add Week to Weeks-Table", error)
                self.disconnectDB()
                return -1, ID

        else:
            self.disconnectDB()
            return 0, ID

    def addDay(self, date):
        '''
        input
            - Date:    datetime Obj  

        return   
            - INT:   -1 Failed, 1 added/updated, 0 exists
            - ID NR: -1 Failed, 0 added,  >0 ID
        '''

        year,week,day = self.getDateSplit(date)
      
        # add Week if not exists
        retcode, weekID = self.addWeek(year,week)
        if retcode < 0:
            return -1,-1

        if (self.connectDB() != 1):
            return -1,-1
        
        # Check if ID is existing  
        cursor = self.connection.execute( f'SELECT * from Days where WEEKS_ID = {weekID} AND DATE = {day}')   
       
        if self.getlength(cursor) == 0:           
            # Entry does not exist
            try: 
                query = "INSERT INTO Days (Date, Start, End, wTime, WEEKS_ID) VALUES (?, ?, ?, ?, ?)"
                param = (day, date.isoformat(), date.isoformat(), 0.0, weekID)    
                self.connection.execute(query, param)
                self.connection.commit()  
                self.disconnectDB()
                return 1,0
            
            except self.connection.Error as error:
                print("Failed to add Day to Days-Table", error)
                self.disconnectDB()
                return -1,-1

        else:
            # Entry Exists
            ID = 0       
            cursor = self.connection.execute( f'SELECT * from Days where WEEKS_ID = {weekID} AND DATE = {day}')            
            for item in cursor:               
                ID = item[0]
            self.disconnectDB()         
            
            return 0, ID
       
    def addTask(self,date, start, end, comment='', project=''):
        '''
        input
            - Date:    datetime Obj  

        return   
            - INT:  -1 Failed, 1 added/updated, 0 exists
            - ID NR: 0 Failed, else >0
        '''

        # add Day if not exists
        retcode, dayID = self.addDay(date)
        if retcode < 0:
            return -1,-1
        if dayID == 0: 
            retcode, dayID = self.addDay(date)       


        if (self.connectDB() != 1):
            return -1,-1
        
        # Check if ID is existing  
        cursor = self.connection.execute( f'SELECT * from Tasks where DAYS_ID = {dayID}')   
       
        # Check if new Time is between an existing entry 
        if start > end:
            print('Time period is not valid')
            return -1,-1

        for item in cursor:     

            start_old = datetime.datetime.fromisoformat(item[1]) 
            end_old   = datetime.datetime.fromisoformat(item[2]) 
            
            if start > start_old and start < end_old:
                print('Time period is not valid')
                return -1,-1
                  

        # Calculate Time in Hours
        dt = (end - start).total_seconds()
        dt = (dt / 60 / 60) 

        try: 
            query = "INSERT INTO Tasks (Start, End, wTime, Comment, Project, DAYS_ID) VALUES (?, ?, ?, ?, ?, ?)"
            param = (start.isoformat(), end.isoformat(), dt,comment, project, dayID)    
            self.connection.execute(query, param)
            self.connection.commit()  
            self.disconnectDB()
            return 1
        
        except self.connection.Error as error:
            print("Failed to add Task in Tasks-Table", error)
            self.disconnectDB()
            return -1


    # Update Tables
    def updateUser(self, sapUser, sapPW, prUser, prPW):
        '''
        return:   INT,  -1 Failed, 1 updated
        '''

        if (self.connectDB() != 1):
            return -1,-1

        # Check if ID is existing  
        cursor = self.connection.execute( f'SELECT * from UserData') 

        if self.getlength(cursor) != 0:
            try:                   
                query = f'UPDATE UserData SET SAPUser= ? , SAPPW=?, PrReportUser=?, PrReportPW=? WHERE ID = {1}'
                data = (sapUser,sapPW,prUser,prPW)
                
                self.connection.execute(query, data)
                self.connection.commit()           
                self.disconnectDB() 
                return 1

            except self.connection.Error as error:
                print("Failed to update UserData", error)
                self.disconnectDB()
                return -1    

    def updateWeek(self,year, week, wTime, prTime):
        '''
        return:   INT,  -1 Failed, 1 updated
        '''
         
        ID = self.getWeekID(year,week)         
        try:
            self.connectDB()               
            query = f'UPDATE Weeks SET wTime=?, PrReportTime=? WHERE ID = {ID}'
            data  = (wTime, prTime)
            self.connection.execute(query, data)
            self.connection.commit()           
            self.disconnectDB() 
            return 1

        except self.connection.Error as error:
            print("Failed to update Database", error)
            self.disconnectDB()
            return -1    
        
    def updateDay(self,date, wTime):
        '''
        input
            - Date:    datetime Obj  
            - wTime:   Float, 0 = calc internal from Tasks

        return   
            INT,  -1 Failed, 1 updated       
        '''

        year,week,day = self.getDateSplit(date)      
        weekID        = self.getWeekID(year, week)       
        
        # Compare with saved data
        _,oldStart, oldEnd, oldwTime = self.getDay(date)
        tasks                        = self.getTasks(date)

        if wTime == 0:           
            for k,item in enumerate(tasks):              
                wTime += item[2]   # Clac wTime from each task          
            # Attention breaks will not be considered                    
                          
        if self.connectDB() != 1:
            return -1
        try:           
            query  = f'UPDATE Days SET  wTime = ?  WHERE WEEKS_ID = ? AND Date=?'        
            data   = (wTime, weekID, day)
            self.connection.execute(query, data) 
            self.connection.commit()   
            self.disconnectDB()   
            return 1 

        except self.connection.Error as error:
            print("Failed to update Days-Database", error)
            self.disconnectDB() 
            return -1
    

    # Get Methods
    def getUser(self):
        '''
            return:   [SAP_User, SAP_PW, PrReport_User, PrReport_PW]
        '''

        if self.connectDB() != 1:
            return [None, None, None, None] 

        # Check if ID is existing  
        cursor = self.connection.execute( f'SELECT * from UserData where ID = {1}') 

        for item in cursor:
            return item[1:]
        
        return [None, None, None, None]   
              
    def getDay(self,date):
        '''
        input
            - Date:    datetime Obj  

        return   
            [Date, Start, End, wTime]  as [int, datetime, datetime, float]           
        '''

        year,week,day = self.getDateSplit(date)      
        weekID        = self.getWeekID(year, week)
        if self.connectDB() != 1:
            return [None, None, None, None] 
        
        # Get ID if exist#
        query  = "SELECT * from Days where WEEKS_ID = ? AND Date=?"
        data   = (weekID, day)
        cursor = self.connection.execute(query, data) 

        for item in cursor:
            self.disconnectDB()
            return item[1:-1]
        
        self.disconnectDB()        
        return [None, None, None, None]

    def getTasks(self, date):
        '''
        input
            - Date:    datetime Obj  

        return   
            data[Start, End, wTime, Comment, Project]  as [datetime, datetime, float, str, str] x Number of Entries          
        '''

        retcode,dayID = self.addDay(date)   
        if retcode != 0:
            print('Failed to get Day ID')
            return [-1,-1,-1,-1,-1]
    
        if (self.connectDB() != 1):
            return [-1,-1,-1,-1,-1]
        
        # Check if ID is existing  
        cursor = self.connection.execute( f'SELECT * from Tasks where DAYS_ID = {dayID}')
        data   = []

        for item in cursor:
            data.append(item[1:-1])

        self.disconnectDB()
        return data    

    def getWeek(self,year, week):
        '''      
        input
            - year:    int
            - week     int
        return   
            [Start, End, wTime]  as [datetime, datetime, float]           
        '''
       
        weekID        = self.getWeekID(year, week)

        if self.connectDB() != 1:
            return [None, None, None] 
        
        # Get ID if exist
        query  = "SELECT * from Weeks where ID = ?"
        data   = (weekID,)
        cursor = self.connection.execute(query, data) 

        for item in cursor:
            return item[1:]
        
        return [None, None, None]

    # delete Tasks
    def delTasks(self, date):
        '''
        input
            - Date:    datetime Obj  

        return   
            1 OK, -1 Failed, 0 Entry not exists
        '''

        retcode,dayID = self.addDay(date)   

        if retcode != 0:
            print('Failed to get Day ID')
            return 0
        
    
        if (self.connectDB() != 1):
            return -1
        
        # Check if ID is existing  
        try:
            print(f'Day ID {dayID}')
            query =  f'DELETE FROM Tasks WHERE DAYS_ID = ?'
            data  = (dayID,)
            cursor = self.connection.execute(query, data)
            self.connection.commit()
            print(f'Tasks deleted: {cursor.rowcount}') 

            self.disconnectDB()
            return 1
        
        except self.connection.Error as error:
            print("Failed to Delete Tasks Entry", error)
            self.disconnectDB() 
            return -1   




#  ------------------------------------------------------------------------------------------------- 
#  -------------------------------------------------------------------------------------------------
#  MAIN
#  ------------------------------------------------------------------------------------------------- 
#  -------------------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     DB = HandleDB(PathDB)   
#     DB.addWeek(2024,12)
#     #DB.addWeek(2024,12)
#     DB.updateWeek(2024,12,10,25)

#     now = datetime.datetime.now()
#     print(DB.addTask(now, now, now, 'Das Habe ich gemacht', 'Das ost mein Projekt'))

#     DB.updateUser("kauste", "stefan.kaufmann@sigmatek.at", '00', '00')

#     print(DB.getUser())

#     print(DB.getDay(now))
#     year, week, day = DB.getDateSplit(now)
#     print(DB.getWeek(year,week))

   
#     print('---------------------------------------- \n  GET Tasks')
    
#     print(  DB.getTasks(now)[0]) 

#     print('---------------------------------------- \n  Update Day')
#     DB.updateDay(now, wTime=10)

#     # print('---------------------------------------- \n  Delete Taks')
#     # DB.delTasks(now)
    
#     ## TODO TEST
