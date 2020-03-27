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

def inputExpenseData():
    expenseDate = expenseDateInput()
    expenseCategory = expenseCategoryInput()
    expenseAmount = expenseAmountInput()
    expenseComment = expenseCommentInput()
    expenseTransource_id = expenseTransource_idInput()
    expenseInvestmentPeriod = expenseInvestmentPeriodInput()

    return Expense(expenseDate, 
                    expenseCategory,
                    expenseAmount,
                    expenseComment,
                    expenseTransource_id,
                    expenseInvestmentPeriod)

# _______________________________________________________
#  <<<<<<<      Expense Date Input Start        >>>>>>>
#________________________________________________________

def expenseDateInput():
    while True:
        dateInput = str(input("\n\n\tPlease enter a date for your expense: \nFORMAT: yyyy-mm-dd"))
        if dateInput.split("-").len() == 3 and \
            dateInput.split("-")[0].len() == 4 and \
            dateInput.split("-")[1].len() == 2 and \
            dateInput.split("-")[2].len() == 2:
            try:
                expenseDate = datetime.date(dateInput)
            except Exception as err:
                print("\n\t*** Failed to convert str to datetime.date object ***\n")
                print(err)
            else:
                print("\n\nYou put in the date: {}\t".format(expenseDate.date))
                correctInput = str(input("\nIs this correct? \ny/n: ")).lower()
                if correctInput == 'y':
                    return expenseDate
        else:
            print("\n****** WARNING ******* \
                    \nInvalid input format \
                    \n********************")
            stillInput = str(input("\nWould you like to try again? \
                                    \ty/n: ")).lower()
            if stillInput != 'y':
                return None


# ____________________________________________________________
#  <<<<<<<      Expense Category Input Start        >>>>>>>
#_____________________________________________________________

def expenseCategoryInput():
    '''
    Function that takes an input (str) from user which then tries to return a category ID (int)
    PARAMETERS: None
    OUTPUT: categoryID (int)
    '''
    categoryListDF = getDataList('categories')

    while True:

        print(categoryListDF)
        categoryInput = int(input("\n\n\tPlease enter the category for the expense. \
                                            \nFORMAT: Number in the 'id' column \
                                            \nEnter category id: "))
        try:
            categoryID = int(categoryListDF['id'][categoryListDF['id'] == categoryInput].iloc[0])
        except Exception as err:
            print("\n\n***************************\
                    \n Could not properly convert category into an ID\
                    \n***************************\n")
            print(err)
            user_choice = input("\n\n Would you like to try another input? \
                        \n\ty/n: ")
            if user_choice == 'n':
                return None
        else:
            return categoryID



# ___________________________________________________________
#  <<<<<<<      Expense Amount Input Start        >>>>>>>
#____________________________________________________________

def expenseAmountInput():
    while True:
        try:
            amount = int(input("\n\tEnter amount (NTD): "))
        except Exception(TypeError) as err:
            print("\n ... If you are going to enter an amount, please enter a NUMBER ...")
            print(err)
            userChoice = str(input("\n\nWould you like to try again?\
                                    \ny/n: "))
            if userChoice == 'n':
                return None
        else:
            return amount
    

# ____________________________________________________________
#  <<<<<<<      Expense Comment Input Start        >>>>>>>
#_____________________________________________________________

def expenseCommentInput():
    while True:
        expenseComment = str(input("Please enter a comment (50): "))
        if len(expenseComment) > 50:
            print("You can only fit 50 characters...")
            continue
        else:
            return expenseComment
        

# _________________________________________________________________
#  <<<<<<<      Expense Transource ID Input Start        >>>>>>>
#__________________________________________________________________

def expenseTransource_idInput():
    tryAgain = ''
    
    while True:
        
        transourceDF = getDataList('transource')

        if transourceDF != None:
            print(transourceDF.head(10))
            try:
                userChoice = int(input("\nIf you see your wanted transource among the entries, please enter its ID: "))
            except Exception(TypeError) as err:
                print("\nTry to put in a number... a-hole.")
                print(err)
            else:
                return userChoice
            
        else:
            print("\nSeems like you weren't able to get a proper transource-table out.")
            tryAgain = str(input("\nWould you like to try again? \
                                    \n\t y/n: ")).lower()
        
        if tryAgain == 'y':
            continue
        else:
            return None




# _________________________________________________________________
#  <<<<<<<      Expense Input :: Get LISTS Start        >>>>>>>
#__________________________________________________________________

def getDataList(type: str=''):
    '''
    A function that simply fetches the data from the table provided in the argument 'type'.
    INPUT: type (str)
    OUTPUT: categoryListDF (pandas.DataFrame)
    '''

    conn = pg2.connect(database='BudgetTracker', user='postgres',
                           password=secret, host='localhost', port='5432')

    if type == 'categories':
        sqlQuery = '''
                    SELECT id, 
                    maincategory_name AS main,
                    subcategory_name AS sub
                    FROM categories
                    ORDER BY id
                    '''

        try:
            categoryListDF = pd.read_sql_query(sqlQuery, conn)
        except Exception as err:
            print("\nFAILED to execute the following SQL query: \n{}".format(sqlQuery))
            print(err)
        else:
            return categoryListDF

    elif type == 'transource':

        searchQuery = str(input("\nPlease enter a few characters to search for (3~6 characters) \
                                    \n\tSearch for: "))
        
        if len(searchQuery) > 3:
            whereClause = "WHERE name LIKE '\%{}\%'".format(searchQuery)
            sqlQuery = '''
                SELECT * FROM transource
                {}
                ORDER BY name
                '''.format(whereClause)
            
            try:
                transourceListDF = pd.read_sql_query(sqlQuery, conn)
            except Exception as err:
                print("\nFAILED to execute the following SQL query: \n{}".format(sqlQuery))
                print(err)
            else:
                return transourceListDF
    else:
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


def menu_updateTransource():
    print("\n\n ****************************************\
            \nThis function is not doing anything anymore...\
            \n***************************************\n\n")



master_input = True
menu_choice = 0


while master_input:
    try:
        menu_choice = int(input(
            "\nWhat would you like to do? \n(input corresponding number) \
                \n\tAdd Data \
                    \n\t\t 11. Expenses \
                    \n\t\t 12. Income \
                    \n\t\t 13. Transaction Source \
                    \n\t\t 14. Bank Account \
                    \n\t\t 15. Loan \
                \n\tEdit Data \
                    \n\t\t 21. Expenses \
                    \n\t\t 22. Income \
                    \n\t\t 23. Transaction Source \
                    \n\t\t 24. Bank Account \
                    \n\t\t 25. Loan \
                \n\tAnalyze Budget \
                    \n\t\t 31. Overall Analysis \
                    \n\t\t 32. Categorical Spending Analysis \
                    \n\t\t 33. Budget Analysis \
                    \n\t\t 34. Future Projectory Analysis \
                \n\tLoad Data \
                \n\tUpdate Data"))
    except Exception as err:
        print("Sorry, we were not able to determine what you would like to do.")
        print(err)
    else:

        # MENU 11 - Add Expenses

        if menu_choice == 11:
            print("\nYou chose 11: Add Expenses\n")
            expense = inputExpenseData()
            print(expense)
            # SAVE THE ENTERED DATA INTO A DATABASE
            expense.addExpense()

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

        # MENU choice 5 - Update Data

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
    finally:
        master_input = (
            input("Would you like to input more data? \n\t'y'/'n' : ").lower() == 'y')


if __name__ == '__main__':
    print("BudgetTracker.py is being run directly.")
else:
    print("BudgetTracker.py was imported.")
