# BudgetTracker
Hey fellas!</p>
Since late last year, I've been working on this project as somehting I could do to practice my Python & data analysis skills while it benefits myself.
However, I have realized in recent days that this project needs (to say the least) some real make-over. It needs to be renovated.

So from now on, I've decided to almost re-write the entire application with the following end goals:

## Structure Reform
<ol>
<li>	Make it more <b>READ</b>able by making most of the application <b>object-oriented</b>	</li>
<li>	Write more extensive <b>documentations</b> on algorithms & functions.	</li>
<li>	Re-organize the <b><i>database</i></b> for much needed clarity in data.	</li>
</ol>

## Menu
<ol>
  <li>Add Data
    <ul>
      <li>Add Expenses</li>
      <li>Add Income</li>
      <li>Add Transaction Source</li>
      <li>Add Bank Account</li>
      <li>Add Loans</li>
      <li>Return to Main Menu</li>
    </ul>
  </li>
  <li>Edit Data
    <ul>
      <li>Edit Expenses</li>
      <li>Edit Income</li>
      <li>Edit Transaction Source</li>
      <li>Edit Bank Account</li>
      <li>Edit Loans</li>
      <li>Return to Main Menu</li>
    </ul>
  </li>
  <li>Analyze Data
    <ul>
      <li>Overall Summary</li>
      <li>Categorical Spending Analysis</li>
      <li>Budget Analysis</li>
      <li>Future Projectory Analysis</li>
      <li>Return to Main Menu</li>
    </ul>
  </li>
  <li>Quit</li>
</ol>

## Content
### Add Data
As the name suggests, anything that will end up on the database will end up under this one menu.
Since the each data has its own way of being represented, there will be sub-menus as below.
#### Add Expenses
This will take user's input to register an expense onto the database which will later be used for different financial analyses.
Expenses all get registered onto a table under the name <i><u>year_record</i></u>.
#### Add Income
Since they're all about adding data to the database, this will be very similar to the above function except that the data the user puts in is obviously slightly different.
#### Add Transaction Source
This is function will definitely be seen used less as time passes by since this is simply a function to add stores/service providers.
A very limited amount of information will be stored about each 'Transaction Source', but there will be some basic information.
Right now it's limited to <b>name</b>, <b>country</b> and <b>area</b> (city/province).
#### Add Bank Account
Yet another function that will be very simple and used less often.
The data from this will be used to project future cash flow and savings for clearer projection of the near future.
#### Add Loans
The priority for this function will be <b>very</b> low for now, but eventually the functionality needs to be there.

### Edit Data
As you can see above, this is simply just a revised version of the above functions and the logic will be very similar.

### Analyze Data
This seciton is heavily relying on the following libraries:
<ul>
  <li>numpy</li>
  <li>Pandas</li>
  <li>matplotlib</li>
  <li>seaborn</li>
  <li>psycopg2</li>
</ul>
#### Overall Summary
