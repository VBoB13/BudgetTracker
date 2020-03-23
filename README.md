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
This is going to provide the user with general spending analysis and plotting it out on different graphs. This function will most likely end up using most of the database in its calculations. This is the general idea is that it should provide:
<ul>
  <li>Full timeline with overall spending, income and total assets.</li>
  <li>Graph that shows money saved each day until today.</li>
  <li>A table that shows these numbers.</li>
</ul>

#### Categorical Analysis
This will be a function that takes the data from the <b><i>year_record</b></i> table where all the individual transactions are stored and perform the following calculations:
<ul>
  <li>Show a graph that shows <i><u>how much of the total budget that each category takes up.</i></u></li>
  <li>Show how much each individual sub-category in <i><u>groceries</i></u> take up compared to total groceries.</li>
  <li>Will add more to this function as I figure out more things</li>
</ul>
  
#### Budget Analysis
This function will have a sole purpose of comparing the user's set numbers against what the current actual numbers state.
The things that will be calculated or shown will be:
<ul>
  <li>Show how each number compare against the user's pre-set budget numbers.</li>
  <li>Future implementations:
  <ul>
    <li>Show user if their saving goals are met with current budget projectory</li>
    <li>Download local consumption data from government statistical websites through API and compare the user's budget against those</li>
  </ul>
  </li>
</ul>

#### Future Projectory
This function will be kind of similar to the Budget Analysis but with more emphasis on future prediction graphs.
As I learn more about Machine Learning, I will most likely implement a bunch of that into the future projectory function, but we shall see as time passes :)

Now when the structure is a little clearer, I will start off with the most obvious task - to make sure the current (messy) main database table <b><u>year_record</b></u> has its transource_id field correctly filled so that each transaction can be related to a source.
  
