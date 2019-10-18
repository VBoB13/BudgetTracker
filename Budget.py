import datetime

class Budget:

    def __init__(self, livingRatio=0.3, expensesRatio=0.5, savingsRatio=0.2):
        self.livingRatio = livingRatio
        self.expensesRatio = expensesRatio
        self.savingsRatio = savingsRatio

    def __str__(self):
        return f"Current Budget Settings: \n\tLiving Costs: {self.livingRatio * 100}%\n\tExpenses: {self.expensesRatio * 100}%\n\tSaving Ratio: {self.savingsRatio * 100}%"

    def addBudget(self):
        pass

if __name__ == '__main__':
	print("Budget.py is being run directly.")
else:
	print("Budget.py was imported.")