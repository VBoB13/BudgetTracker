import datetime

class RecurringCost:

	def __init__(self, name, category, start_date, stop_date, frequency, amount):
		self.name = name
		self.category = category
		self.start_date = start_date
		self.stop_date = stop_date
		self.frequency = frequency
		self.amount = amount

	def __str__(self):
		return f"{self.name}\n\tCategory: {self.category}\n\tStart Date: {self.start_date}\n\tEnd Date: {self.stop_date}\n\tFrequency (per month): {self.frequency}\n\tAmount: {self.amount}"

	def editName(self, name):
		self.name = name

	def editCategory(self, category):
		self.category = category

	def editStartDate(self, start_date):
		self.start_date = start_date

	def editStopDate(self, stop_date):
		self.stop_date = stop_date

	def editFrequency(self, frequency):
		self.frequency = frequency

	def editAmount(self, amount):
		self.amount = amount

	

if __name__ == '__main__':
	print("Recurring Costs.py is being run directly.")
else:
	print("Recurring Costs.py was imported.")