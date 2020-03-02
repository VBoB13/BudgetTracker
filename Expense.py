import datetime
import psycopg2 as pg2
from FileLoader import FileLoader

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


class Expense:

    def __init__(self, time, category, amount, comment='', transource='', investment_period=1):
        self.time = time
        self.category = category
        self.amount = amount
        self.comment = comment
        self.transource = transource
        self.investment_period = investment_period

    def __str__(self):
        return f"\n -- Details --\n\t${self.amount} NT \n\tCategory: {self.category} \n\tTime: {self.time} \n\tComment: {self.comment}\n\t Transaction source: {self.transource}\n\tInvestment period: {self.investment_period} months\n"

    def editTime(self, time):
        self.time = time

    def editCategory(self, category):
        self.category = category

    def editAmount(self, amount):
        self.amount = amount

    def editComment(self, comment):
        self.comment = comment

    def addExpense(self):

        if self.category in category_check_list.keys():
            print(f"\n{self.category} found in Check List\n")
            category_id = category_check_list.get(self.category)

            conn = pg2.connect(database='BudgetTracker', user='postgres',
                               password=secret, host='localhost', port='5432')
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO year_record (datetime, category, category_id, amount, comment_text, transource, investment_period) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (self.time,
                     self.category,
                     category_id,
                     self.amount,
                     self.comment,
                     self.transource,
                     self.investment_period))
            except Exception as err:
                print("Was not able to add data to database")
                print(err)
            else:
                conn.commit()
            finally:
                conn.close()

        else:
            print(
                f"\nCould not find {self.category} in Check List \nNo data added to database")
            return None


if __name__ == '__main__':
    print("Expense.py is being run directly.")
else:
    print("Expense.py was imported.")
