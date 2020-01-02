from FileLoader import FileLoader
import datetime
from calendar import monthrange
import psycopg2 as pg2
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


pwfile = FileLoader("pass.txt")
secret = pwfile.loadPass()

category_check_list = {
    'Living': 11,
    'Food': 12,
    'Medical': 13,
    'Transportation': 14,
    'Kitties': 15,
    'Shopping': 21,
    'Entertainment': 22,
    'Sport': 23,
    'Travel': 24,
    'Misc': 25,
    'Debt': 31,
    'Savings': 32,
    'Income': 41,
    'Other Income': 42}


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

    def __str__(self):
        if self.avgDailySpending == 0:
            return f"\n\n ------------------------------ \n\n -- Current Budget Settings -- \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%\n\n -- General Income & Spending Data --\n\tCurrent month income: {self.thisMonthIncome}\n\tDaily Income (avg): {self.avgDailyIncome}\n\n ------------------------------ \n\n"
        else:
            return f"\n\n ------------------------------ \n\n -- Current Budget Settings -- \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%\n\n -- General Income & Spending Data --\n\tCurrent month income: {self.thisMonthIncome}\n\tDaily Income (avg): {self.avgDailyIncome}\n\tDaily Spending (avg): {self.avgDailySpending}\n\n ------------------------------ \n\n"

    def getLastMonthToday(self):
        today = datetime.date.today()

        # Checks to see whether the previous month has less amount of days than the current one
        # If it has less days, then the date is subtracted by the amount of days that the current month has MORE than the previous one
        # This then gets converted into a string for later use in database
        # queries
        if monthrange(
                today.year,
                today.month -
                1)[1] < monthrange(
                today.year,
                today.month)[1]:
            maxDaysDiff = monthrange(today.year, today.month)[
                1] - monthrange(today.year, today.month - 1)[1]
            self.lastMonthToday = str(today.replace(
                month=(today.month - 1), day=(today.day - maxDaysDiff)))
        else:
            self.lastMonthToday = str(today.replace(month=(today.month - 1)))

        print(self.lastMonthToday)

    def getThisMonthIncome(self):
        '''
        Function used to initialize the budget ratios every time the application starts.
        This is simply to always have a budget ready to be used in calculations and (later) determine whether the user needs any spending behavior changed.
        '''
        totalIncome = 0

        conn = pg2.connect(database='BudgetTracker', user='postgres',
                           password=secret, host='localhost', port='5432')

        query = '''
                SELECT datetime, 
                    (amount/investment_period) AS inv_amount,
                    investment_period,
                    category_id
                FROM 
                    year_record
                WHERE 
                    category_id > 40
                ORDER BY 
                    datetime DESC
                '''

        try:
            incomeDF = pd.read_sql_query(query, conn)
        except Exception as err:
            print("\n\t-- Was not able to add data to database --")
            print(f"\t Error: {err}\n")
        else:

            for inv_period in range(1,25):
                today = datetime.date.today()
                pastDate = today - datetime.timedelta(days=(31*inv_period))
                print(f"\n\nChecking income data since {pastDate} with investment_period = {inv_period}")
                totalIncome += incomeDF['inv_amount'][(
                                                        incomeDF['datetime'] >= pastDate) & (
                                                        incomeDF['investment_period'] == inv_period)].sum()

            self.thisMonthIncome = totalIncome
            self.avgDailyIncome = format(
                totalIncome / (monthrange(today.year, today.month)[1]), '.1f')
            print(self)
        finally:
            conn.close()

    def getTotalSpending(self):

        conn = pg2.connect(database='BudgetTracker', user='postgres',
                           password=secret, host='localhost', port='5432')

        query = '''
                SELECT datetime, 
                    (amount/investment_period) AS inv_amount,
                    investment_period,
                    category_id
                FROM 
                    year_record
                WHERE 
                    category_id < 30
                ORDER BY 
                    datetime DESC
                '''

        try:
            spendingDF = pd.read_sql_query(query, conn)
        except Exception as err:
            print("\n\t-- Was not able to add data to database --")
            print(f"\t Error: {err}\n")
        else:

            for inv_period in range(1,25):
                today = datetime.date.today()
                pastDate = self.getStartDate(inv_period)
                print(f"\n\nChecking spending data since {pastDate} with investment_period = {inv_period}")
                totalSpending += spendingDF['inv_amount'][(
                                                        spendingDF['datetime'] >= pastDate) & (
                                                        spendingDF['investment_period'] == inv_period)].sum()

            self.totalSpending = totalSpending
            self.avgDailySpending = format(
                totalSpending / (monthrange(today.year, today.month)[1]), '.1f')
            print(self)
        finally:
            conn.close()

    def getStartDate(self, num_months):
        
        today = datetime.date.today()

        if today.month <= num_months:
            monthsDiff = abs(today.month - num_months)
            if monthsDiff < 12:
                
                # Getting the lowest number of maximum days in either the current month or the 'target' month
                lastDateOfMonth = min([
                                        monthrange(today.year - 1, 12 - monthsDiff)[1], 
                                        monthrange(today.year, today.month)[1]
                                        ])

                startDate = today.replace(today.year - 1, 12 - monthsDiff, min([lastDateOfMonth, today.day]))
            else:
                # Getting the lowest number of maximum days in either the current month or the 'target' month
                lastDateOfMonth = min([monthrange(today.year - 2, 24 - monthsDiff)[1], 
                                        monthrange(today.year, today.month)[1]])

                startDate = today.replace(today.year - 2, 24 - monthsDiff, min([lastDateOfMonth, today.day]))

        else:
            monthsDiff = abs(today.month - num_months)
            # Getting the lowest number of maximum days in either the current month or the 'target' month
            lastDateOfMonth = min([
                                    monthrange(today.year - 1, 12 - monthsDiff)[1], 
                                    monthrange(today.year, today.month)[1]
                                    ])
            startDate = today.replace(today.year, 12 - monthsDiff, min([lastDateOfMonth, today.day]))

        return startDate


    def getPandasDataFrame(self):
        conn = pg2.connect(database='BudgetTracker', user='postgres',
                           password=secret, host='localhost', port='5432')
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
            print("\n\n\t -- Error: Couldn't execute SQL query to import data as Pandas DataFrame --\n\n")
            print(err)

        else:
            self.sqlSpendingData = pd.read_sql_query(sql, conn)

        finally:
            conn.close()

    def getTimeFrameMeans(self):

        today = datetime.date.today()
        oneMonth = datetime.timedelta(
            days=(monthrange(today.year, today.month)[1]))
        oneDay = datetime.timedelta(days=1)
        lastMonth = today - oneMonth

        dailySpendingMeans = []
        dailyCategoryMeansDict = {
            'Living': [],
            'Food': [],
            'Medical': [],
            'Transportation': [],
            'Kitties': [],
            'Shopping': [],
            'Entertainment': [],
            'Sport': [],
            'Travel': [],
            'Misc': []}

        dateDiff = (today - self.sqlSpendingData['datetime'].iloc[0]).days
        dateList = pd.date_range(
            pd.to_datetime(
                self.sqlSpendingData['datetime'].iloc[0]),
            periods=dateDiff).tolist()

        avgRent = self.getRentDailyAvg()

        for date in dateList:

            dayPrior = date - oneDay
            dayAfter = date + oneDay

            filteredDataFrame = self.sqlSpendingData['inv_amount'][
                (self.sqlSpendingData['datetime'] >= dayPrior) & (
                    self.sqlSpendingData['datetime'] <= dayAfter) & (
                    self.sqlSpendingData['category_id'] < 40) & (
                    self.sqlSpendingData['investment_period'] == 1) & (
                    self.sqlSpendingData['comment_text'] != 'Rent')]
            dailySpendingMeans.append(round(((filteredDataFrame.sum() + avgRent*3) / 3), 1))

            for key, value in category_check_list.items():

                if value < 30:
                    categoricalDataFrame = self.sqlSpendingData['inv_amount'][
                        (self.sqlSpendingData['datetime'] >= dayPrior) & (
                            self.sqlSpendingData['datetime'] <= dayAfter) & (
                            self.sqlSpendingData['category_id'] == value) & (
                            self.sqlSpendingData['investment_period'] == 1) & (
                            self.sqlSpendingData['comment_text'] != 'Rent')]
                    categoryLongTerm = 0

                    for inv_period in range(2, 25, 1):
                        pastDate = today - \
                            datetime.timedelta(days=(30 * inv_period))
                        categoryLongTerm += self.sqlSpendingData['inv_amount'][
                            (self.sqlSpendingData['datetime'] >= pastDate) & (
                                self.sqlSpendingData['investment_period'] == inv_period) & (
                                self.sqlSpendingData['category_id'] == value)].sum()

                    if value == 11:
                        dailyCategoryMeansDict[key].append(int(
                            round(((categoricalDataFrame.sum() + categoryLongTerm + avgRent*3) / 3), 1)))
                    else:
                        dailyCategoryMeansDict[key].append(
                            int(round(((categoricalDataFrame.sum() + categoryLongTerm) / 3), 1)))

        for key, value in dailyCategoryMeansDict.items():
            print(f"\n{key}:\n{value}\n")

        dailyCategoryMeansDF = pd.DataFrame(
            dailyCategoryMeansDict, index=dateList)
        print(
            f"\n----------------------------\n\n{dailyCategoryMeansDF}\n\n----------------------------\n")

        incomeList = []
        for i in range(len(dateList)):
            incomeList.append(self.avgDailyIncome)

        dailyCategoryMeansDF.insert(len(
            dailyCategoryMeansDF.columns), 'Avg. Daily Spending', dailySpendingMeans, True)
        dailyCategoryMeansDF.insert(
            len(dailyCategoryMeansDF.columns), 'Avg. Daily Income', incomeList, True)

        dailyCategoryMeansDF = dailyCategoryMeansDF.loc[self.lastMonthToday:]

        print(
            f"\n----------------------------\n\n{dailyCategoryMeansDF}\n\n----------------------------\n")

        return dailyCategoryMeansDF

    def analyzePandasDataFrame(self):
        dailyCategoryMeansDF = self.getTimeFrameMeans()
        dailyCategoryMeansDF.plot()

        plt.legend(dailyCategoryMeansDF.columns)
        plt.xlabel('Time')
        plt.ylabel('Amount (NTD)')

        if int(
            dailyCategoryMeansDF['Avg. Daily Spending'].max()) > int(
            float(
                self.avgDailyIncome)):
            ymax = int(dailyCategoryMeansDF['Avg. Daily Spending'].max())
        else:
            ymax = int(float(self.avgDailyIncome))

        axes = plt.gca()
        axes.set_ylim(0, ymax)
        plt.show()

    def spendingAnalysis(self):
        self.getPandasDataFrame()
        self.analyzePandasDataFrame()

    def getBudgetPandasDataFrame(self):

        conn = pg2.connect(database='BudgetTracker', user='postgres',
                           password=secret, host='localhost', port='5432')
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
        # Therefore, double rents need to be checked for and taken in to
        # account when making the budget calculations.
        avgDailyRent = self.getRentDailyAvg()

        budgetDict = {'Income %': [0, 0, 0, 0]}

        for invNum in range(1, 25, 1):
            startDate = self.getStartDate(invNum)

            budgetDict['Income %'][0] += int(
                round((self.sqlBudgetData['amount_inv'][
                        (self.sqlBudgetData['category_id'] < 20) & (
                            self.sqlBudgetData['investment_period'] == invNum) & (
                            self.sqlBudgetData['datetime'] >= startDate)
                            ].sum()),2))
            budgetDict['Income %'][1] += int(
                round(
                    (self.sqlBudgetData['amount_inv'][
                        (self.sqlBudgetData['category_id'] > 20) & (
                            self.sqlBudgetData['category_id'] < 30) & (
                            self.sqlBudgetData['investment_period'] == invNum) & (
                            self.sqlBudgetData['datetime'] >= startDate)
                            ].sum()),2))
            budgetDict['Income %'][2] += int(
                round(
                    (self.sqlBudgetData['amount_inv'][
                        (self.sqlBudgetData['category_id'] > 30) & (
                            self.sqlBudgetData['category_id'] < 40) & (
                            self.sqlBudgetData['investment_period'] == invNum) & (
                            self.sqlBudgetData['datetime'] >= startDate)
                            ].sum()),2))

        budgetDict['Income %'][0] = int(
            round((budgetDict['Income %'][0] / self.thisMonthIncome), 2) * 100)
        budgetDict['Income %'][1] = int(
            round((budgetDict['Income %'][1] / self.thisMonthIncome), 2) * 100)
        budgetDict['Income %'][2] = int(
            round((budgetDict['Income %'][2] / self.thisMonthIncome), 2) * 100)

        if (budgetDict['Income %'][0] +
            budgetDict['Income %'][1] +
                budgetDict['Income %'][2]) >= 100:
            budgetDict['Income %'][3] = 0
        else:
            budgetDict['Income %'][3] = int(100 -
                                            int(budgetDict['Income %'][0]) -
                                            int(budgetDict['Income %'][1]) -
                                            int(budgetDict['Income %'][2]))

        budgetIndexList = ['Living', 'Expenses', 'Debts & Savings', 'Rest']

        budgetDF = pd.DataFrame(budgetDict, index=budgetIndexList)
        print(budgetDF)

        budgetDF.plot.pie(y='Income %')
        budgetDF.plot.bar()
        plt.show()

    def getRentDailyAvg(self):

        rentThisMonth = 0
        totalRent = 0
        today = datetime.date.today()
        daysInCurrentMonth = monthrange(today.year, today.month)[1]

        try:
            self.sqlSpendingData['amount'][(
                self.sqlSpendingData['comment_text'] == 'Rent')].sum()
        except Exception:
            print("No Spending Data available, using Budget Data instead.")
            totalRent = self.sqlBudgetData['amount'][(
                self.sqlBudgetData['comment_text'] == 'Rent')].sum()
            rentThisMonth = totalRent / \
                len(self.sqlBudgetData['amount'][(
                    self.sqlBudgetData['comment_text'] == 'Rent')].index)
        else:
            totalRent = self.sqlSpendingData['amount'][(
                self.sqlSpendingData['comment_text'] == 'Rent')].sum()
            rentThisMonth = totalRent / \
                len(self.sqlSpendingData['amount'][(
                    self.sqlSpendingData['comment_text'] == 'Rent')].index)
        finally:

            return int(round((rentThisMonth / daysInCurrentMonth),0))

    def budgetAnalysis(self):
        self.getBudgetPandasDataFrame()
        self.analyzeBudget()


if __name__ == '__main__':
    print("Budget.py is being run directly.")
else:
    print("Budget.py was imported.")
