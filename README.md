# Capstone repo
# Trello Board: https://trello.com/b/rlook2ar

# Run Project Help
When grabbing project from github:
1) Open the project up in IDE
2) Go to file/settings
3) Go to Project: capstoneproj tab (Left side panel)
4) Go to Python Interpreter
5) Click the gear next to python interpreter dropdown
6) Click Add
7) Make sure base interpreter is the location of the your python.exe on your computer (Ex: C:\Users\<User>\AppDate\Local\Programs\Python`\`)
8) Apply changes and hit okay
9) From the terminal in PyCharm nagivate to venv/scripts
10) Type activate to activate environment
11) Then pip install -r <location of requirements.txt>
12) Still in venv type: git clone https://github.com/openai/gym.git
14) Then: cd gym
15) Then: pip install -e .
16) Finally: pip install finrl
17) Once all downloads are complete navigate back to capstone\capstoneproj\capstone type: py manage.py runserver
18) Server should now be running


# Setup run from play button (Pycharm)
1) Right when you open up the project (In pycharm atleast) there is a dropdown right next to the play button
2) Click that dropdown and hit edit configurations
3) hit the plus sign on the top left to add a python file
4) Name it whatever you like
5) Find the manage.py file in the project (Ex: C:\Users\<User>\Documents\GitHub\capstone\capstoneproj\capstone\manage.py)
6) Add in parameters field: runserver
7) Set Python Interpreter with your new interpreter you created with the steps above this
8) Set working directory (Ex: C:\Users\<user>\Documents\GitHub\capstone\capstoneproj\capstone)
9) Now the play button should run a local server on your computer and you can now view the app

## QA Testing: 
For QA tests, code must be ran in VS Code along side the project running in PyCharm. You'll need to install WebDriver and change the variable to point to where you installed it. The Create account tests will fail now that we added email authentication.

