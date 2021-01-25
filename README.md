# Capstone repo
# Trello Board: https://trello.com/b/rlook2ar

# Run Project Help
When grabbing project from github:
1) Open the project up in IDE
2) Delete venv folder
3) Go to file/settings
4) Go to Project: capstoneproj tab (Left side panel)
5) Go to Python Interpreter
6) Click the gear next to python interpreter dropdown
7) Click Add
8) Make sure base interpreter is the location of the your python.exe on your computer (Ex: C:\Users`\`<User>\AppDate\Local\Programs\Python`\`)
9) Apply changes and hit okay
10) Then on that same python interpreter screen (file/settings/Project: capstoneproj/)
11) Click the plus sign on the bottom left and add the following packages:
12) django, django-crispy-forms, and six (Updated as of 1/25)

# Setup run from play button (Pycharm)
1) Right when you open up the project (In pycharm atleast) there is a dropdown right next to the play button
2) Click that dropdown and hit edit configurations
3) hit the plus sign on the top left to add a python file
4) Name it whatever you like
5) Find the manage.py file in the project (Ex: C:\Users`\`<User>\Documents\GitHub\capstone\capstoneproj\capstone\manage.py)
6) Add in parameters field: runserver
7) Set Python Interpreter with your new interpreter you created with the steps above this
8) Set working directory (Ex: C:\Users`\`<user>\Documents\GitHub\capstone\capstoneproj\capstone)
9) Now the play button should run a local server on your computer and you can now view the app

