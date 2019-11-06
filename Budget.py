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


    def getPandasDataFrame(self):
        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        try:
            sql = f'''SELECT datetime, amount, category_id FROM year_record 
                WHERE datetime > '{self.lastMonthToday}'
                AND datetime >= '2019-10-18'
                AND datetime <= '{str(datetime.date.today())}'
                AND category_id < 40
                ORDER BY datetime, category_id, amount;'''

        except Exception as err:
            print("Couldn't execute SQL query to import data as Pandas DataFrame")
            print(err)

        else:
            self.sqldata = pd.read_sql_query(sql, conn)

        finally:
            conn.close()

    def getTimeFrameMeans(self):
        
        print(self.sqldata)
        print(f"-- {self.sqldata.datetime.iloc[0]}\n\t -> {type(self.sqldata.datetime.iloc[0])}")
        print(self.sqldata.datetime.iloc[5] - self.sqldata.datetime.iloc[0])
        date_difference = self.sqldata.datetime.iloc[5] - self.sqldata.datetime.iloc[0]
        print(date_difference.days)
        print(self.sqldata.datetime.iloc[0].day)
        print(self.sqldata.datetime.iloc[0].month)
        print(self.sqldata.datetime.iloc[0].days_in_month)


        dailySpendingMeans = []
        dailyCategoryMeansDict = {'Living':[], 'Food':[], 'Medical':[], 'Transportation':[], 'Kitties':[], 'Shopping':[], 'Entertainment':[], 'Sport':[], 'Travel':[], 'Misc':[]}
        dateDiff = (pd.datetime.today() - self.sqldata.datetime.iloc[0]).days
        dateList = pd.date_range(pd.to_datetime(self.sqldata.datetime.iloc[0]), periods=dateDiff).tolist()
        
        for date in dateList:
            if (date.day < date.days_in_month) and (date.day > 1):
                dayPrior = date.replace(date.year, date.month, date.day-1)
                dayAfter = date.replace(date.year, date.month, date.day+1)
                dayPriorString = f"{dayPrior.year}-{dayPrior.month}-{dayPrior.day}"
                dayAfterString = f"{dayAfter.year}-{dayAfter.month}-{dayAfter.day}"
                filteredDataFrame = self.sqldata['amount'][(self.sqldata['datetime'] >= dayPriorString) & (self.sqldata['datetime'] <= dayAfterString)]
                dailySpendingMeans.append(filteredDataFrame.sum() / 3)

                for key, value in category_check_list.items():
                    if value < 30:
                        categoricalDataFrame =  self.sqldata['amount'][(self.sqldata['datetime'] >= dayPriorString) & (self.sqldata['datetime'] <= dayAfterString) & (self.sqldata.category_id == value)]
                        dailyCategoryMeansDict[key].append(round((categoricalDataFrame.sum() / 3), 3))


            elif date.day == 1:
                dayPrior = date.replace(date.year, (date.month)-1, date.replace(date.year, (date.month)-1).days_in_month)
                dayAfter = date.replace(date.year, date.month, date.day+1)
                dayPriorString = f"{dayPrior.year}-{dayPrior.month}-{dayPrior.day}"
                dayAfterString = f"{dayAfter.year}-{dayAfter.month}-{dayAfter.day}"
                filteredDataFrame = self.sqldata['amount'][(self.sqldata['datetime'] >= dayPriorString) & (self.sqldata['datetime'] <= dayAfterString)]
                dailySpendingMeans.append(filteredDataFrame.sum() / 3)

                for key, value in category_check_list.items():
                    if value < 30:
                        categoricalDataFrame =  self.sqldata['amount'][(self.sqldata['datetime'] >= dayPriorString) & (self.sqldata['datetime'] <= dayAfterString) & (self.sqldata.category_id == value)]
                        dailyCategoryMeansDict[key].append(round((categoricalDataFrame.sum() / 3), 3))

            else:
                dayPrior = date.replace(date.year, date.month, date.day-1)
                dayAfter = date.replace(date.year, (date.month)+1, 1)
                dayPriorString = f"{dayPrior.year}-{dayPrior.month}-{dayPrior.day}"
                dayAfterString = f"{dayAfter.year}-{dayAfter.month}-{dayAfter.day}"
                filteredDataFrame = self.sqldata['amount'][(self.sqldata['datetime'] >= dayPriorString) & (self.sqldata['datetime'] <= dayAfterString)]
                dailySpendingMeans.append(filteredDataFrame.sum() / 3)

                for key, value in category_check_list.items():
                    if value < 30:
                        categoricalDataFrame =  self.sqldata['amount'][(self.sqldata['datetime'] >= dayPriorString) & (self.sqldata['datetime'] <= dayAfterString) & (self.sqldata.category_id == value) & (self.sqldata.investment_period <= 1)]
                        dailyCategoryMeansDict[key].append(int(round((categoricalDataFrame.sum() / 3), 0)))

        for key, value in dailyCategoryMeansDict.items():
                print(f"\n{key}:\n{value}\n")

        dailyCategoryMeansDF = pd.DataFrame(dailyCategoryMeansDict, index=dateList)
        print(f"\n----------------------------\n\n{dailyCategoryMeansDF}\n\n----------------------------\n")

        incomeList = []
        for i in range(len(dateList)):
            incomeList.append(self.avgDailyIncome)

        dailyCategoryMeansDF.insert(0, 'Avg. Daily Spending', dailySpendingMeans, True)
        dailyCategoryMeansDF.insert(0, 'Avg. Daily Income', incomeList, True)

        print(f"\n----------------------------\n\n{dailyCategoryMeansDF}\n\n----------------------------\n")
        
        return dailyCategoryMeansDF

    def analyzePandasDataFrame(self):
        dailyCategoryMeansDF = self.getTimeFrameMeans()

        
        for column in dailyCategoryMeansDF.columns:
            plt.plot(dailyCategoryMeansDF.index, dailyCategoryMeansDF[column])

        plt.legend(dailyCategoryMeansDF.columns)
        plt.xlabel('Time')
        plt.ylabel('Amount (NTD)')

        if int(dailyCategoryMeansDF['Avg. Daily Spending'].max()) > int(float(self.avgDailyIncome)):
            ymax = int(dailyCategoryMeansDF['Avg. Daily Spending'].max())
        else:
            ymax = int(self.avgDailyIncome)

        axes = plt.gca()
        axes.set_ylim([0,ymax])
        plt.show()



    def spendingAnalysis(self):
        self.getLastMonthToday()
        self.getTotalSpending()
        self.getAvgDailySpending()
        self.getPandasDataFrame()
        self.analyzePandasDataFrame()


if __name__ == '__main__':
	print("Budget.py is being run directly.")
else:
	print("Budget.py was imported.")