from FileLoader import FileLoader
import datetime
from calendar import monthrange
import csv
import psycopg2 as pg2
from psycopg2.extras import execute_values as pg2_execute_values
import pandas as pd
import numpy as np

from Expense import Expense
from RecurringCost import RecurringCost
from Income import Income
from Budget import Budget

pwfile = FileLoader("pass.txt")
secret = pwfile.loadPass()


def inputExpense(expenseInfo):
    '''
    This function simply takes the expense input (string) from the user and splits, converts and uploads it (if input is correct) to the database.
    INPUT: expenseInfo (string)
    Output: expense (Expense)
    '''

    try:
        # Attempts to split the input data to later decipher and handle
        expenseInfoList = expenseInfo.split(',')
    except Exception as err:
        # Error that's printed if that does not go well.
        print("Wasn't able to properly derive values from input.")
        print(err)
    else:
        if len(expenseInfoList[0]) == 8 and len(expenseInfoList) <= 6:
            try:
                # If the date-spot in the list has the correct length, we attempt to extract the value of entered year, month and date
                # through list index slicing and directly put it into a
                # variable that is of the class 'datetime'
                expenseDate = datetime.date(int(expenseInfoList[0][0:4]), int(
                    expenseInfoList[0][4:6]), int(expenseInfoList[0][6:8]))
            except Exception as err:
                print(
                    "Something went wrong when trying to convert input date format to datetime-class.")
                print(err)
            else:
                print("datetime-class convertion successful.")
                try:
                    # Attempt to put the category-data that was prompted by the
                    # user into 'expenseCategory'
                    expenseCategory = expenseInfoList[1]
                except Exception as err:
                    print("Wasn't able to load category data into variable.")
                    print(err)
                else:
                    try:
                        # Attempt to put the amount that was prompted by the
                        # user into 'expenseAmount'
                        expenseAmount = int(expenseInfoList[2])
                    except Exception as err:
                        print(
                            "Wasn't able to load expense amount data into variable.")
                        print(err)
                    else:
                        try:
                            # Attempt to put the comment-data that was prompted
                            # by the user into 'expenseComment'
                            expenseComment = expenseInfoList[3]
                        except Exception as err:
                            print(
                                "Wasn't able to load expense comment data into variable.")
                            print(err)
                        else:
                            print(
                                "Successfully loaded all data into variables.\n Attempting to create Expense object.")
                            # Creating an Expense object called 'expense' for
                            # convenience.
                            if len(expenseInfoList) == 5:
                                expense = Expense(
                                    expenseDate, expenseCategory, expenseAmount, expenseComment)
                                return expense
                            else:
                                try:
                                    expense_inv_period = int(
                                        expenseInfoList[4])
                                    expenseTransource = str(expenseInfoList[5])
                                except Exception as err:
                                    print(
                                        "Couldn't convert investment_period data into Python variable.")
                                    print(err)
                                else:
                                    expense = Expense(
                                        expenseDate,
                                        expenseCategory,
                                        expenseAmount,
                                        expenseComment,
                                        expenseTransource,
                                        expense_inv_period)
                                    return expense

        else:
            print("Invalid input. (ExpenseInfoList too long/short)")
            print(
                "Please enter a date such as if the current date is Oct 7, 2019, enter '20191007'")
            return None


def inputRecurringExpense():
    pass


def inputIncome(incomeInfo):
    '''
    This function simply takes the income input from the user and splits, converts and uploads it (if input is correct) to the database.
    INPUT: incomeInfo (string)
    Output: income (Income)
    '''

    try:
        # Attempts to split the input data to later decipher and handle
        incomeInfoList = incomeInfo.split(',')
    except Exception as err:
        # Error that's printed if that does not go well.
        print("Wasn't able to properly derive values from input.")
        print(err)
    else:
        if len(incomeInfoList[0]) == 8 and len(incomeInfoList) <= 5:
            try:
                # If the date-spot in the list has the correct length, we attempt to extract the value of entered year, month and date
                # through list index slicing and directly put it into a
                # variable that is of the class 'datetime'
                incomeDate = datetime.date(int(incomeInfoList[0][0:4]), int(
                    incomeInfoList[0][4:6]), int(incomeInfoList[0][6:8]))
            except Exception as err:
                print(
                    "Something went wrong when trying to convert input date format to datetime-class.")
                print(err)
            else:
                try:
                    # Attempt to put the category-data that was prompted by the
                    # user into 'incomeCategory'
                    incomeCategory = incomeInfoList[1]
                except Exception as err:
                    print("Wasn't able to load category data into variable.")
                    print(err)
                else:
                    try:
                        # Attempt to put the amount that was prompted by the
                        # user into 'incomeAmount'
                        incomeAmount = int(incomeInfoList[2])
                    except Exception as err:
                        print("Wasn't able to load income amount data into variable.")
                        print(err)
                    else:

                        try:
                            # Attempt to put the comment-data that was prompted
                            # by the user into 'incomeComment'
                            incomeComment = incomeInfoList[3]
                        except Exception as err:
                            print(
                                "Wasn't able to load income comment data into variable.")
                            print(err)
                        else:
                            # Creating an income object called 'income' for
                            # convenience.
                            if len(incomeInfoList) == 4:
                                income = Income(
                                    incomeDate, incomeCategory, incomeAmount, incomeComment)
                                return income
                            else:
                                try:
                                    # Attempt to put the investment period that
                                    # was prompted by the user into
                                    # 'investment_period'
                                    incomeInvestmentPeriod = incomeInfoList[4]
                                except Exception as err:
                                    print(
                                        "Wasn't able to load income investment period data into variable.")
                                    print(err)
                                else:
                                    # Creating an income object called 'income'
                                    # for convenience.
                                    income = Income(
                                        incomeDate,
                                        incomeCategory,
                                        incomeAmount,
                                        incomeComment,
                                        incomeInvestmentPeriod)
                                    return income

        else:
            print("Invalid date input (too long/short).")
            print(
                "Please enter a date such as if the current date is Oct 7, 2019, enter '20191007'")
            return None


def fileLoader(month):
    try:
        with open(f'{month}.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f"{'    '.join(row)}")

                print(f"{row['Year']} \t{row['Month']} \t {row['Date']} \t {row['Living']} \t   {row['Food']}\t   {row['Medical']}\t      {row['Transportation']}\t\t{row['Kitties']} \t   {row['Shopping']} \t       {row['Entertainment']} \t\t{row['Sport']} \t {row['Misc.']} \t  {row['Travel']} \t    {row['Debts']} \t     {row['Savings']} \t\t{row['Income']}")
                for key, value in row:
                    if (row[key] != 0) and (key != 'Year') and (
                            key != 'Month') and (key != 'Date'):
                        pass

                line_count += 1

    except Exception as err:
        print("\nSomething went wrong when trying to load the file.\nPlease make sure the file exists.")
        print(err)

    else:
        print("\n\tData retrieval successful!")


def updateTransourceTable_getData():
    conn = pg2.connect(database='BudgetTracker', user='postgres',
                        password=secret, host='localhost', port='5432')
    query = '''
                SELECT * FROM transource
                ORDER BY id;
                '''
    
    try:
        transourceDF = pd.read_sql_query(query, conn)
    except Exception as err:
        print("\n\n *** Wasn't able to fetch data from TABLE 'transource' ***\n\n")
        print(err)
    else:
        return transourceDF

def updateTransourceTable(transourceDF):
    print("\n\n --- UPDATING transource TABLE --- \n\n")

    firstID = transourceDF['id'].iloc[0]
    lastID = transourceDF['id'].iloc[-1]
    maxID = transourceDF['id'].size

    print("First ID:\t{}\nLast ID:\t{}\nDF Max Index:\t{}".format(firstID, lastID, maxID))
    
    transourceDF['area'] = transourceDF['name'].apply(updateTransourceTable_transourceArea)
    transourceDF['country'] = transourceDF['name'].apply(updateTransourceTable_transourceCountry)
    transourceDF['name'] = transourceDF['name'].apply(updateTransourceTable_transourceName)

    print(transourceDF)

    print("\n\n\t********************\
                \n\tStarting Updates\
                \n\t********************\n")
    transourceDF_tuple = tuple(zip(transourceDF.name, transourceDF.area, transourceDF.country, transourceDF.id))
    print(transourceDF_tuple)
    updateTransourceTable_SQL(transourceDF_tuple)

def updateTransourceTable_SQL(transourceDF_tuple):
    conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
    conn.autocommit = True
    cur = conn.cursor()

    try:
        update_query = """UPDATE transource AS t 
                            SET name = e.name,
                            area = e.area,
                            country = e.country
                            FROM (VALUES %s) AS e(name, area, country, id) 
                            WHERE e.id = t.id;"""

        pg2_execute_values(cur, update_query, transourceDF_tuple, template=None, page_size=100)

    except Exception as err:
        print("\n\t*** *** *** *** *** \
                \n\tSQL UPDATE ERROR\
                \n\t*** *** *** *** ***\n\n")
        print(err)
    finally:
        conn.close()

def updateTransourceTable_transourceName(transourceText):
    if '-' in transourceText:
        return transourceText.split('-')[0]
    else:
        return transourceText

def updateTransourceTable_transourceArea(transourceText):
    if '-' in transourceText:
        
        transourceLocation = transourceText.split('-')[1]
        if '(' in transourceLocation:
            transourceArea = transourceLocation.split('(')[0]
            return transourceArea
        else:
            return ''

    else:
        return ''

def updateTransourceTable_transourceCountry(transourceText):
    if '-' in transourceText:
        
        transourceLocation = transourceText.split('-')[1]
        if '(' in transourceLocation:
            transourceCountry = transourceLocation.split('(')[1].replace(')','')
            return transourceCountry
        else:
            return ''

    else:
        return ''


def menu_updateTransource():
    data = updateTransourceTable_getData()
    updateTransourceTable(data)



master_input = True
menu_choice = 0


while master_input:
    try:
        menu_choice = int(input(
            "\nWhat would you like to do? \n(input corresponding number) \n\n\t1: Expenses \n\t2: Income \n\t3: Analyze Budget\n\t4: Load Data\n\t5: Update Data"))
    except Exception as err:
        print("Sorry, we were not able to determine what you would like to do.")
        print(err)
    else:

        # MENU choice 1 - Expenses

        if menu_choice == 1:
            print("\nYou chose 1: Expenses\n")

            while True:
                try:
                    expenseInput = int(input(
                        "\nWhat would you like to do with Expenses?\n\t1: Add Expenses\n\t2: Update Expense Data\n\t3: Delete Expense Data\n\t4: Main Menu\n\n\tYour choice: "))
                except Exception as err:
                    print("\nTry using a number.. works better that way. Dumbass.\n")
                    print(err)
                else:

                    if 1 <= expenseInput <= 3:
                        while expenseInput == 1:

                            expenseInfo = input("Please enter the necessary information about the expense in the following format:\n\t date,category,amount,comment(, investment period)\n\tAs in: 20191007,Food,500,Dinner\n\t-- OR --\n\tAs in: 20191007,Food,500,Dinner,12 (for 12 months investment period)\n\tIf there's no input for Investment Period, the value will automatically be set to 1.\n\n\t Enter your expense data: ")
                            expense = inputExpense(expenseInfo)
                            if expense is not None:
                                print(expense)
                                # SAVE THE ENTERED DATA INTO A DATABASE
                                expense.addExpense()

                            if input(
                                    "Would you like to input more expenses?\n\t'y'/'n' : ").lower() == 'y':
                                continue
                            else:
                                expenseInput = 0
                                break
                    elif expenseInput == 4:
                        break
                    else:
                        break


        # MENU choice 2 - Income

        elif menu_choice == 2:
            print("\nYou chose 2: Income\n")
            incomeInput = True
            while incomeInput:
                income = inputIncome(incomeInfo=input(
                    "\nPlease enter the necessary information about the income in the following format:\n\t date,category,amount,comment\n\tAs in: 20191007,Food,500,Dinner\n\n\t Enter your income data: "))
                print(income)

                if income is not None:
                    # SAVE THE ENTERED DATA INTO A DATABASE
                    income.addIncome()

                if input(
                        "\nWould you like to input more incomes?\n\t'y'/'n' : ").lower() == 'y':
                    incomeInput = True
                else:
                    incomeInput = False


        # MENU choice 3 - Analyze Budget

        elif menu_choice == 3:
            print("\nYou chose 3: Analyze Budget")
            currentBudget = Budget()

            while True:
                try:
                    budget_choice = int(input(
                        "\t Put in the number for the kind of alanysis you would like: \n1 : Spending Analysis\n2 : Budget & Saving Analysis\n3 : Budget Settings\n4 : Back to Main Menu\n\n\tYour Choice: "))
                except Exception as err:
                    print("\n\t <<< Stick to the NUMBERS... Keyword: NUMBERS >>>")
                    print(err)
                else:
                    if budget_choice == 1:
                        currentBudget.spendingAnalysis()
                    elif budget_choice == 2:
                        currentBudget.budgetAnalysis()
                    else:
                        break


        # MENU choice 4 - Load Data

        elif menu_choice == 4:
            print("\nYou chose 4: Load Data")

            dataLoad = True
            while dataLoad:
                fileLoader(month=input(
                    "\nType the month that you want to import into the database.\n\tNote that the file has to be in the same folder as the application itself and must be CSV format.\n\tMonth: "))

                if input("\nWould you like to load data from other files?\n\t'y'/'n' : ").lower() == 'y':
                    dataLoad = True
                else:
                    dataLoad = False

        elif menu_choice == 5:
            print("\nYou chose 5: Update Data\n")

            updateData = True
            while updateData:
                menu_updateTransource()

                if input("\nWould you like to update data AGAIN?!\n\t'y'/'n' : ").lower() == 'y':
                    updateData = True
                else:
                    updateData = False

        else:
            print("\nPlease, make a valid menu choice (1-5).")
            continue

    master_input = (
        input("Would you like to input more data? \n\t'y'/'n' : ").lower() == 'y')


if __name__ == '__main__':
    print("BudgetTracker.py is being run directly.")
else:
    print("BudgetTracker.py was imported.")
