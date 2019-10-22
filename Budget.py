import datetime
from calendar import monthrange
import psycopg2 as pg2
import pandas as pd
import matplotlib as plt

secret = 'R1cJ3nn@10/19'
category_check_list = {'Living':11, 'Food':12, 'Medical':13, 'Transportation':14, 'Kitties':15, 'Shopping':21, 'Entertainment':22, 'Sport':23, 'Travel':24, 'Misc':25, 'Debt':31, 'Savings':32, 'Income':41, 'Other Income':42}

class Budget:

    livingRatio = 0.3
    expensesRatio = 0.5
    savingsRatio = 0.2
    thisMonthIncome = 0
    avgDailyIncome = 0
    avgDailySpending = 0

    def __init__(self):
        pass

    def __str__(self):
        return f"Current Budget Settings: \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%\n\tCurrent month income: {self.thisMonthIncome}\n\tDaily Income (avg): {self.avgDailyIncome}\n\tDaily Spending (avg): {self.avgDailySpending}"

    def getThisMonthIncome(self):
        '''
        Function used to initialize the budget ratios every time the application starts.
        This is simply to always have a budget ready to be used in calculations and (later) determine whether the user needs any spending behavior changed.
        '''
        today = datetime.date.today()
        if monthrange(today.year, today.month - 1)[1] < monthrange(today.year, today.month)[1]:
            maxDaysDiff = monthrange(today.year, today.month)[1] - monthrange(today.year, today.month - 1)[1]
            lastMonthToday = str(today.replace(month=today.month - 1, day=today.day - maxDaysDiff))
        else:
            lastMonthToday = str(today.replace(month=today.month - 1))
            
        print(lastMonthToday)
        
        totalIncome = 0

        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        cur = conn.cursor()

        query = "SELECT SUM(amount) FROM year_record WHERE datetime > '%s' AND (category LIKE 'Income')"

        try:
            cur.execute(query % lastMonthToday)
        except Exception as err:
            print("\n\t-- Was not able to add data to database --")
            print(f"\t Error: {err}\n")
        else:
            incomeSQL = cur.fetchall()
            for row in incomeSQL:
                totalIncome = row[0]
            
            print(totalIncome)
            self.thisMonthIncome = totalIncome
            self.avgDailyIncome = totalIncome/(monthrange(today.year,today.month))
        finally:
            conn.close()

    def getAvgDailySpending(self):
        currentYearLastMonth = datetime.date.today()
        lastMonthToday = str(currentYearLastMonth.replace(month=currentYearLastMonth.month-1))

        conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
        cur = conn.cursor()
        query = "SELECT ROUND(AVG(amount),1) FROM year_record WHERE datetime > '%s' AND (category_id != 41) AND (category_id != 42)"

        try:
            cur.execute(query % lastMonthToday)
        except Exception as err:
            print("\nSomething clearly went wrong here...")
            print(f"\n\t{err}")
        else:
            result = cur.fetchone()
            print(result)
        finally:
            conn.close()

        self.avgDailySpending = result
    
    def spendingAnalysis(self):
        self.getAvgDailySpending()



    



if __name__ == '__main__':
	print("Budget.py is being run directly.")
else:
	print("Budget.py was imported.")