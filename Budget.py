import datetime
from calendar import monthrange
import psycopg2 as pg2
import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

from FileLoader import FileLoader

pwfile = FileLoader("pass.txt")
secret = pwfile.loadPass()

category_check_list = {'Living':11, 'Food':12, 'Medical':13, 'Transportation':14, 'Kitties':15, 'Shopping':21, 'Entertainment':22, 'Sport':23, 'Travel':24, 'Misc':25, 'Debt':31, 'Savings':32, 'Income':41, 'Other Income':42}

class Budget:

    livingRatio = 0.35
    expensesRatio = 0.45
    savingsRatio = 0.2
    thisMonthIncome = 0
    avgDailyIncome = 0
    totalSpending = 0
    avgDailySpending = 0
    lastMonthToday = ""
    categorizedSpendingThisMonth = {}
    sqlSpendingData = pd.DataFrame
    sqlBudgetData = pd.DataFrame


    def __init__(self):
        self.getLastMonthToday()
        self.getThisMonthIncome()
        self.getTotalSpending()
        self.getAvgDailySpending()

    def __str__(self):
        if self.avgDailySpending == 0:
            return f"\n\n ------------------------------ \n\n -- Current Budget Settings -- \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%\n\n -- General Income & Spending Data --\n\tCurrent month income: {self.thisMonthIncome}\n\tDaily Income (avg): {self.avgDailyIncome}\n\n ------------------------------ \n\n"
        else:
            return f"\n\n ------------------------------ \n\n -- Current Budget Settings -- \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%\n\n -- General Income & Spending Data --\n\tCurrent month income: {self.thisMonthIncome}\n\tDaily Income (avg): {self.avgDailyIncome}\n\tDaily Spending (avg): {self.avgDailySpending}\n\n ------------------------------ \n\n"
    
    def getLastMonthToday(self):
        today = datetime.date.today()

        # Checks to see whether the previous month has less amount of days than the current one
        # If it has less days, then the date is subtracted by the amount of days that the current month has MORE than the previous one
        # This then gets converted into a string for later use in database queries
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

        query = '''
                SELECT SUM(amount) FROM year_record 
                WHERE datetime > '%s' 
                AND category_id > 40
                '''

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
        query = '''
                SELECT SUM(amount) FROM year_record 
                WHERE datetime > '%s' 
                AND category_id <= 31
                '''

        try:
            cur.execute(query % self.lastMonthToday)
        except Exception as err:
            print("\nSomething clearly went wrong here...")
            print(f"\n\t{err}")
        else:
            result = cur.fetchone()
            print(f"Total Spending since {self.lastMonthToday}:\n\t${result[0]} NT\n\n")
        finally:
            conn.close()

        self.totalSpending = result[0]

    def getAvgDailySpending(self):
        
        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        cur = conn.cursor()
        query = "SELECT ROUND(AVG(amount),1) FROM year_record WHERE datetime > '%s' AND category_id < 30"

        try:
            cur.execute(query % self.lastMonthToday)
        except Exception as err:
            print("\nSomething clearly went wrong here...")
            print(f"\n\t{err}")
        else:
            result = cur.fetchone()
            print(f"Avg. Daily Spending since {self.lastMonthToday}: {result[0]} \n\t(Excluding 'Debts & Savings') \n\n")
        finally:
            conn.close()

        self.avgDailySpending = result[0]


    def getPandasDataFrame(self):
        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        try:
            sql = f'''SELECT 
                        datetime, 
                        amount, 
                        (amount/investment_period) AS inv_amount, 
                        category_id, 
                        investment_period,
                        comment_text
                    FROM year_record 
                    WHERE 
                        category_id < 40
                    ORDER BY 
                        datetime, 
                        category_id, 
                        amount;'''

        except Exception as err:
            print("Couldn't execute SQL query to import data as Pandas DataFrame")
            print(err)

        else:
            self.sqlSpendingData = pd.read_sql_query(sql, conn)

        finally:
            conn.close()

    def getTimeFrameMeans(self):
        
        today = datetime.date.today()
        oneMonth = datetime.timedelta(days=(monthrange(today.year, today.month)[1]))
        lastMonth = today - oneMonth
        dailySpendingMeans = []
        dailyCategoryMeansDict = {'Living':[], 'Food':[], 'Medical':[], 'Transportation':[], 'Kitties':[], 'Shopping':[], 'Entertainment':[], 'Sport':[], 'Travel':[], 'Misc':[]}
        dateDiff = (today - self.sqlSpendingData.datetime.iloc[0]).days
        dateList = pd.date_range(pd.to_datetime(self.sqlSpendingData.datetime.iloc[0]), periods=dateDiff).tolist()
        
        doubleRent = (self.checkForDoubleRent(self.sqlSpendingData['datetime'].iloc[0]) / 30)

        for date in dateList:
            if (date.day < date.days_in_month) and (date.day > 1):
                dayPrior = date.replace(date.year, date.month, date.day-1)
                dayAfter = date.replace(date.year, date.month, date.day+1)
                filteredDataFrame = self.sqlSpendingData['inv_amount'][(self.sqlSpendingData['datetime'] >= dayPrior) & (self.sqlSpendingData['datetime'] <= dayAfter) & (self.sqlSpendingData['category_id'] < 40) & (self.sqlSpendingData['investment_period'] == 1)]
                dailySpendingMeans.append(round((filteredDataFrame.sum() / 3), 1))

                for key, value in category_check_list.items():
                    if value < 30:
                        categoricalDataFrame =  self.sqlSpendingData['inv_amount'][(self.sqlSpendingData['datetime'] >= dayAfter) & (self.sqlSpendingData['datetime'] <= dayAfter) & (self.sqlSpendingData.category_id == value) & (self.sqlSpendingData['investment_period'] == 1)]
                        dailyCategoryMeansDict[key].append(round((categoricalDataFrame.sum() / 3), 1))


            elif date.day == 1:
                dayPrior = date.replace(date.year, (date.month)-1, date.replace(date.year, (date.month)-1).days_in_month)
                dayAfter = date.replace(date.year, date.month, date.day+1)
                filteredDataFrame = self.sqlSpendingData['inv_amount'][(self.sqlSpendingData['datetime'] >= dayPrior) & (self.sqlSpendingData['datetime'] <= dayAfter) & (self.sqlSpendingData['category_id'] < 40) & (self.sqlSpendingData['investment_period'] == 1)]
                dailySpendingMeans.append(round((filteredDataFrame.sum() / 3), 1))

                for key, value in category_check_list.items():
                    if value < 30:
                        categoricalDataFrame =  self.sqlSpendingData['inv_amount'][(self.sqlSpendingData['datetime'] >= dayPrior) & (self.sqlSpendingData['datetime'] <= dayAfter) & (self.sqlSpendingData.category_id == value) & (self.sqlSpendingData['investment_period'] == 1)]
                        dailyCategoryMeansDict[key].append(round((categoricalDataFrame.sum() / 3), 1))

            else:
                dayPrior = date.replace(date.year, date.month, date.day-1)
                dayAfter = date.replace(date.year, (date.month)+1, 1)
                filteredDataFrame = self.sqlSpendingData['inv_amount'][(self.sqlSpendingData['datetime'] >= dayPrior) & (self.sqlSpendingData['datetime'] <= dayAfter) & (self.sqlSpendingData['category_id'] < 40) & (self.sqlSpendingData['investment_period'] == 1)]
                dailySpendingMeans.append(round((filteredDataFrame.sum() / 3), 1))

                for key, value in category_check_list.items():
                    
                    if value < 30:
                        categoricalDataFrame =  self.sqlSpendingData['inv_amount'][(self.sqlSpendingData['datetime'] >= dayPrior) & (self.sqlSpendingData['datetime'] <= dayAfter) & (self.sqlSpendingData.category_id == value) & (self.sqlSpendingData['investment_period'] == 1)]
                        categoryLongTerm = 0
                        
                        for inv_period in range(2,25,1):
                            pastDate = today - datetime.timedelta(days=(30*inv_period))
                            categoryLongTerm += self.sqlSpendingData['inv_amount'][(self.sqlSpendingData['datetime'] >= pastDate) & (self.sqlSpendingData['investment_period'] == inv_period) & (self.sqlSpendingData['category_id'] == value)].sum()

                        if value == 11:
                            dailyCategoryMeansDict[key].append(int(round(((categoricalDataFrame.sum() + categoryLongTerm - doubleRent) / 3), 1)))
                        else:
                            dailyCategoryMeansDict[key].append(int(round(((categoricalDataFrame.sum() + categoryLongTerm) / 3), 1)))

        for key, value in dailyCategoryMeansDict.items():
                print(f"\n{key}:\n{value}\n")

        dailyCategoryMeansDF = pd.DataFrame(dailyCategoryMeansDict, index=dateList)
        print(f"\n----------------------------\n\n{dailyCategoryMeansDF}\n\n----------------------------\n")

        incomeList = []
        for i in range(len(dateList)):
            incomeList.append(self.avgDailyIncome)

        dailyCategoryMeansDF.insert(len(dailyCategoryMeansDF.columns), 'Avg. Daily Spending', dailySpendingMeans, True)
        dailyCategoryMeansDF.insert(len(dailyCategoryMeansDF.columns), 'Avg. Daily Income', incomeList, True)

        dailyCategoryMeansDF = dailyCategoryMeansDF.loc[self.lastMonthToday:]

        print(f"\n----------------------------\n\n{dailyCategoryMeansDF}\n\n----------------------------\n")
        
        return dailyCategoryMeansDF

    def analyzePandasDataFrame(self):
        dailyCategoryMeansDF = self.getTimeFrameMeans()
        dailyCategoryMeansDF.plot()
        

        plt.legend(dailyCategoryMeansDF.columns)
        plt.xlabel('Time')
        plt.ylabel('Amount (NTD)')

        if int(dailyCategoryMeansDF['Avg. Daily Spending'].max()) > int(float(self.avgDailyIncome)):
            ymax = int(dailyCategoryMeansDF['Avg. Daily Spending'].max())
        else:
            ymax = int(float(self.avgDailyIncome))

        axes = plt.gca()
        axes.set_ylim(0,ymax)
        plt.show()

    def spendingAnalysis(self):
        self.getPandasDataFrame()
        self.analyzePandasDataFrame()

    def getBudgetPandasDataFrame(self):
        
        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        try:
            sql = f'''SELECT 
                            datetime, 
                            amount, 
                            (amount/investment_period) AS amount_inv, 
                            category_id, 
                            investment_period, 
                            comment_text 
                    FROM 
                            year_record
                    WHERE 
                            category_id < 40
                    ORDER BY 
                            datetime, 
                            category_id, 
                            amount;'''

        except Exception as err:
            print("Couldn't execute SQL query to import data as Pandas DataFrame")
            print(err)

        else:
            self.sqlBudgetData = pd.read_sql_query(sql, conn)

        finally:
            conn.close()

        print(self.sqlBudgetData.head())

    def analyzeBudget(self):
        '''
        This function has its sole purpose of analyzing the Budget Data available and comparing it to the budget settings that the user has set
        '''
        today = datetime.date.today()
        startDate = today

        # Due to uncertainties concerning the dates we pay rent, there may be occasions where jumping a month back in time might include double rents.
        # Therefore, double rents need to be checked for and taken in to account when making the budget calculations.
        doubleRent = self.checkForDoubleRent(self.sqlBudgetData['datetime'].iloc[0])

        budgetDict = {'Income %':[0,0,0,0]}

        for invNum in range(1,25,1):
            if today.month <= invNum:
                monthsDiff = abs(today.month - invNum)
                if monthsDiff < 12:
                    startDate = today.replace(today.year - 1, 12-monthsDiff)
                else:
                    startDate = today.replace(today.year - 2, 24-monthsDiff)
            else:
                monthsDiff = abs(today.month - invNum)
                startDate = today.replace(today.year, today.month - monthsDiff)

            budgetDict['Income %'][0] += int(round((self.sqlBudgetData['amount_inv'][(self.sqlBudgetData['category_id'] < 20) & (self.sqlBudgetData['investment_period'] == invNum) & (self.sqlBudgetData['datetime'] >= startDate)].sum()),2))
            budgetDict['Income %'][1] += int(round((self.sqlBudgetData['amount_inv'][(self.sqlBudgetData['category_id'] > 20) & (self.sqlBudgetData['category_id'] < 30) & (self.sqlBudgetData['investment_period'] == invNum) & (self.sqlBudgetData['datetime'] >= startDate)].sum()),2))
            budgetDict['Income %'][2] += int(round((self.sqlBudgetData['amount_inv'][(self.sqlBudgetData['category_id'] > 30) & (self.sqlBudgetData['category_id'] < 40) & (self.sqlBudgetData['investment_period'] == invNum) & (self.sqlBudgetData['datetime'] >= startDate)].sum()),2))

        budgetDict['Income %'][0] = int(round(((budgetDict['Income %'][0] - doubleRent) / self.thisMonthIncome),2)*100)
        budgetDict['Income %'][1] = int(round((budgetDict['Income %'][1] / self.thisMonthIncome),2)*100)
        budgetDict['Income %'][2] = int(round((budgetDict['Income %'][2] / self.thisMonthIncome),2)*100)

        if (budgetDict['Income %'][0] + budgetDict['Income %'][1] + budgetDict['Income %'][2]) >= 100:
            budgetDict['Income %'][3] = 0
        else:
            budgetDict['Income %'][3] = int(100 - int(budgetDict['Income %'][0]) - int(budgetDict['Income %'][1]) - int(budgetDict['Income %'][2]))

        budgetIndexList = ['Living', 'Expenses', 'Debts & Savings', 'Rest']

        budgetDF = pd.DataFrame(budgetDict, index=budgetIndexList)
        print(budgetDF)

        budgetDF.plot.pie(y='Income %')
        budgetDF.plot.bar()
        plt.show()

    def checkForDoubleRent(self, date):
        
        rentThisMonth = 0

        today = datetime.date.today()
        timeDiff = abs(today - date)
        startDate = today - timeDiff

        print(startDate)

        try:
            self.sqlSpendingData['amount'][(self.sqlSpendingData['comment_text'] == 'Rent') & (self.sqlSpendingData['datetime'] >= startDate)].sum()
        except Exception:
            print("No Spending Data available, using Budget Data instead.")
            rentThisMonth = self.sqlBudgetData['amount'][(self.sqlBudgetData['comment_text'] == 'Rent') & (self.sqlBudgetData['datetime'] >= startDate)].sum()
        else:
            rentThisMonth = self.sqlSpendingData['amount'][(self.sqlSpendingData['comment_text'] == 'Rent') & (self.sqlSpendingData['datetime'] >= startDate)].sum()
        finally:
            if rentThisMonth >= 36000:
                print("\n\t DOUBLE RENT THIS MONTH\n")
                return int(rentThisMonth/2)
            else:
                return 0

    def budgetAnalysis(self):
        self.getBudgetPandasDataFrame()
        self.analyzeBudget()


if __name__ == '__main__':
	print("Budget.py is being run directly.")
else:
	print("Budget.py was imported.")