By Aditya Kelekar, updated: 9.10.2026

# PROJECT DESCRIPTION: 
Hello, this is Aditya, a software engineer and the creator of this project.

The purpose of this project is to develop software to visualize geodata trails. 
A side aim is to compare different cloud providers's services for hosting this project.
The project website is currently under construction and will be updated in a week's time.  

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
1.  Currently analysis of the route with respect to detection of s-bends is shown;
   this functionality could be extended to also detect u-bends (the code for that is already created)
2.  Display the parts of the route that have non-zero "S_BEND" column values on the map.
3.  Provide a feature for the user to add a trail log file (coordinates of a trail) to be plotted.

Please write to me at aditya.kelekar@gmail.com for contributions and suggestions. 
Thank you!

