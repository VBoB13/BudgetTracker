import datetime
import psycopg2 as pg2

secret = 'R1cJ3nn@10/19'

class Budget:

    livingRatio = 0.3
    expensesRatio = 0.5
    savingsRatio = 0.2
    thisMonthIncome = 0

    def __init__(self):
        pass

    def __str__(self):
        return f"Current Budget Settings: \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%\n\tCurrent month income: {self.thisMonthIncome}"

    def getThisMonthIncome(self):
        '''
        Function used to initialize the budget ratios every time the application starts.
        This is simply to always have a budget ready to be used in calculations and (later) determine whether the user needs any spending behavior changed.
        '''
        currentYearLastMonth = datetime.date.today()
        lastMonthToday = str(currentYearLastMonth.replace(month=currentYearLastMonth.month-1))
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
        finally:
            conn.close()



if __name__ == '__main__':
	print("Budget.py is being run directly.")
else:
	print("Budget.py was imported.")