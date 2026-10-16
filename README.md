By Aditya Kelekar, updated: 9.10.2026

# PROJECT DESCRIPTION: 
Hello, this is Aditya, a software engineer and the creator of this project.

The purpose of this project is to develop software to visualize geodata trails. 
A side aim is to compare different cloud providers's services for hosting this project.
The project website is: https://shipshape-511316.lm.r.appspot.com/shipsept/bargraphs/ 
The wiki has notes about the algorithms developed for this project.

Currently, the program displays the route between Helsinki and Talinn based on open-source ship data.
Detection of s-bends and u-bends along the routes is also available, displayed as command line output by running this program locally.
More features are under construction and will be updated every week.  

Potential users are academicians, researchers and, of course, fellow software engineers. 

# INSTALLATION AND RUNNING THE PROJECT:
If you would like to set this project up on your machine, I will guide you through the steps.

1. Create a virtual environment
2. Clone this project: git clone https://github.com/adikele/ships_in_the_sea
3. Using the terminal: move into the same directory that contains the file "manage.py" (this is the inner ship-route-plotter-master directory)
4. Install dependencies: pip install -r requirements.txt
5. Run the program: (on Mac) `python3 manage.py runserver`
6. To check if program works successfully: 
When the program is run with the above-mentioned command, the expected output: 
(i) visit the page (http://127.0.0.1:8000/shipsept/bargraphs/) and choose one of the two radio options:
A partial map of Finland with one of two routes will appear; these are the partial routes of two ships
(ii) analysis of the route with respect to detection of s-bends and u-bends is available, currently seen as command line output.

# TO DO:
1. Feature development: 
(i) Currently analysis of the route with respect to detection of s-bends is displayed in command line output;
   this functionality could be extended to also detect u-bends (the code for that is already created)
(ii) Display the parts of the route that have non-zero "S_BEND" column values on the map.
(iii)  Provide a feature for the user to be able to input a trail log file (coordinates of a trail) to be plotted.

2. Software engineering: 
(i) Create a cloud database for holding input details (ship’s trails) --> currently stored in a csv file
(ii) Use different service providers’ infrastructure to compare cost-efficiency and ease of use (eg. aws-lambda-functions and google-cloud-functions)
(iii) Create a micro service that cleans a user-entered csv file and loads it to a cloud database. Another service could then polls the db if new data is loaded -- if yes, the service would inform the website application about it. The user could then choose (click) to process the data from the csv file for displaying a route map.


Please write to me at aditya.kelekar@gmail.com for contributions and suggestions. 
Thank you!

