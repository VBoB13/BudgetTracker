import datetime
import psycopg2 as pg2

secret = 'R1cJ3nn@10/19'
category_check_list = {'Income':41, 'Other Income':42}

class Income:

	def __init__(self, time, category, amount, comment):
		self.time = time
		self.category = category
		self.amount = amount
		self.comment = comment

	def __str__(self):
		return f"\n\t{self.amount} received on {self.time}\n\tCategory: {self.category}\n\tComment: {self.comment}"

	def editSource(self, category):
		self.category = category

	def editIncome(self, amount):
		self.amount = amount

	def editTime(self, time):
		self.time = time

	def addIncome(self):
		if self.category in category_check_list.keys():
			print(f"\n{self.category} found in Check List\n")
			category_id = category_check_list.get(self.category)

			conn = pg2.connect(database='BudgetTracker', user='postgres', password=secret, host='localhost', port='5432')
			cur = conn.cursor()
			try:
				cur.execute("INSERT INTO year_record (datetime, category, category_id, amount, comment_text) VALUES (%s, %s, %s, %s, %s)", (self.time, self.category, category_id, self.amount, self.comment))
			except Exception as err:
				print("Was not able to add data to database")
				print(err)
			else:
				conn.commit()
			finally:
				conn.close()


		else:
			print(f"\nCould not find {self.category} in Check List \nNo data added to database")
			return None




if __name__ == '__main__':
	print("Income.py is being run directly.")
else:
	print("Income.py was imported.")