import datetime
from calendar import monthrange
import psycopg2 as pg2
import pandas as pd
from matplotlib import pyplot as plt

from FileLoader import FileLoader

pwfile = FileLoader("pass.txt")
secret = pwfile.loadPass()

category_check_list = {'Living':11, 'Food':12, 'Medical':13, 'Transportation':14, 'Kitties':15, 'Shopping':21, 'Entertainment':22, 'Sport':23, 'Travel':24, 'Misc':25, 'Debt':31, 'Savings':32, 'Income':41, 'Other Income':42}

class Budget:

    livingRatio = 0.3
    expensesRatio = 0.5
    savingsRatio = 0.2
    thisMonthIncome = 0
    avgDailyIncome = 0
    totalSpending = 0
    avgDailySpending = 0
    lastMonthToday = ""
    categorizedSpendingThisMonth = {}
    sqldata = pd.DataFrame

    def __init__(self):
        pass

    def __str__(self):
        if self.avgDailySpending == 0:
            return f"\n\n-- Current Budget Settings -- \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%\n\n -- General Income & Spending Data --\n\tCurrent month income: {self.thisMonthIncome}\n\tDaily Income (avg): {self.avgDailyIncome}\n"
        else:
            return f"\n\n-- Current Budget Settings -- \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%\n\n -- General Income & Spending Data --\n\tCurrent month income: {self.thisMonthIncome}\n\tDaily Income (avg): {self.avgDailyIncome}\n\tDaily Spending (avg): {self.avgDailySpending}\n"
    
    def getLastMonthToday(self):
        today = datetime.date.today()

        # Checks to see whether the previous month has less amount of days than the current one
        # If it has less days, then the date is subtracted by the amount of days that the current month has MORE than the previous one
        # This then gets converted into a string for later use in database query
        if monthrange(today.year, today.month - 1)[1] < monthrange(today.year, today.month)[1]:
            maxDaysDiff = monthrange(today.year, today.month)[1] - monthrange(today.year, today.month - 1)[1]
            self.lastMonthToday = str(today.replace(month=(today.month - 1), day=(today.day - maxDaysDiff)))
        else:
            self.lastMonthToday = str(today.replace(month=(today.month - 1)))

        print(self.lastMonthToday)

    def getThisMonthIncome(self):
        '''
        Function used to initialize the budget ratios every time the application starts.
        This is simply to always have a budget ready to be used in calculations and (later) determine whether the user needs any spending behavior changed.
        '''
        today = datetime.date.today()
        totalIncome = 0

        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        cur = conn.cursor()

        query = "SELECT SUM(amount) FROM year_record WHERE datetime > '%s' AND (category LIKE 'Income')"
        print(self.lastMonthToday)

        try:
            cur.execute(query % self.lastMonthToday)
        except Exception as err:
            print("\n\t-- Was not able to add data to database --")
            print(f"\t Error: {err}\n")
        else:
            incomeSQL = cur.fetchone()
            for row in incomeSQL:
                totalIncome = row
            
            self.thisMonthIncome = totalIncome
            self.avgDailyIncome = format(totalIncome/(monthrange(today.year,today.month)[1]), '.1f')
            print(self)
        finally:
            conn.close()

    def getTotalSpending(self):
        
        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        cur = conn.cursor()
        query = "SELECT SUM(amount) FROM year_record WHERE datetime > '%s' AND (category_id != 41) AND (category_id != 42)"

        try:
            cur.execute(query % self.lastMonthToday)
        except Exception as err:
            print("\nSomething clearly went wrong here...")
            print(f"\n\t{err}")
        else:
            result = cur.fetchone()
            print(f"Total Spending since {self.lastMonthToday}: {result[0]}")
        finally:
            conn.close()

        self.totalSpending = result[0]

    def getAvgDailySpending(self):
        
        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        cur = conn.cursor()
        query = "SELECT ROUND(AVG(amount),1) FROM year_record WHERE datetime > '%s' AND (category_id != 41) AND (category_id != 42)"

        try:
            cur.execute(query % self.lastMonthToday)
        except Exception as err:
            print("\nSomething clearly went wrong here...")
            print(f"\n\t{err}")
        else:
            result = cur.fetchone()
            print(f"Avg. Daily Spending since {self.lastMonthToday}: {result[0]}")
        finally:
            conn.close()

        self.avgDailySpending = result[0]
    
    def getCategorizedSpendingThisMonth(self):
        today = datetime.date.today()
        query = '''SELECT SUM(amount) 
                    FROM year_record 
                    WHERE datetime > '%s' 
                    AND category_id = %s'''

        print("\n")
        
        for key, value in category_check_list.items():

            if value != 41 or value != 42:

                conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
                cur = conn.cursor()

                try:
                    cur.execute(query % (self.lastMonthToday, value))
                except Exception as err:
                    print("\nSomething clearly went wrong here...")
                    print(f"\n\t{err}")
                else:
                    result = cur.fetchone()
                finally:
                    conn.close()

                if result[0] == None:
                    totalCategorySpending = 0
                else:
                    totalCategorySpending = result[0]

                print(f"{key}: {totalCategorySpending}")

                self.categorizedSpendingThisMonth[key] = {'Total':totalCategorySpending, 'Daily Avg':format((totalCategorySpending/(monthrange(today.year,today.month)[1])), '.1f'), 'Spending Ratio':format((totalCategorySpending/self.totalSpending), '.1f')}


    def getPandasDataFrame(self):
        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        try:
            sql = f'''SELECT datetime, amount, category_id FROM year_record 
                WHERE datetime > '{self.lastMonthToday}'
                AND datetime >= '2019-10-18'
                AND datetime < '{str(datetime.date.today())}'
                AND category_id != 41
                AND category_id != 42
                ORDER BY datetime, category_id, amount;'''

        except Exception as err:
            print("Couldn't execute SQL query to import data as Pandas DataFrame")
            print(err)

        else:
            self.sqldata = pd.read_sql_query(sql, conn)

        finally:
            conn.close()

    def getTimeFrameMeans(self):
        uniqueDateList = self.sqldata.datetime.unique()
        
        matchingAmountList = []

        print(f"-- {self.sqldata.datetime.iloc[0]}\n\t -> {type(self.sqldata.datetime.iloc[0])}")
        print(self.sqldata.datetime.iloc[5] - self.sqldata.datetime.iloc[0])
        print(self.sqldata.datetime.iloc[0].day)

        dailySums = []
        '''print(self.sqldata.datetime.iloc)
        for dateIndex in self.sqldata.datetime.iloc:
            self.sqldata.datetime.iloc[dateIndex]'''
        


        print(self.sqldata)
        print(f"{uniqueDateList}\n\n{matchingAmountList}")
        return (uniqueDateList, matchingAmountList)

    def analyzePandasDataFrame(self):
        (time, amount) = self.getTimeFrameMeans()



    def spendingAnalysis(self):
        self.getLastMonthToday()
        self.getTotalSpending()
        self.getAvgDailySpending()
        #self.getCategorizedSpendingThisMonth()
        self.getPandasDataFrame()
        self.analyzePandasDataFrame()


if __name__ == '__main__':
	print("Budget.py is being run directly.")
else:
	print("Budget.py was imported.")