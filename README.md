# Givel

## Requirements:
- Vagrant
- VirtualBox

## Getting Started:
1. Clone the repository.
2. Open terminal and navigate inside vagrant directory and run `vagrant up`. 
   This may take a while if run for the first time.
3. Then run `vagrant ssh` to ssh into the virtual machine.
4. To navigate to the project directory from inside the vagrant machine
   `cd /vagrant/givel`. This is where you will see the project directory.

##To install requirements with python3-pip
- `sudo pip3 install -r requirements.txt`


*After the requirements are installed, configure the database*


**IMPORTANT**: Use Python3 to run the application. 

**Steps to run app**
- Run the following command:
   `alias python=python3`
- To run the application, execute the following command:
   `python run.py`


**Shutting down vagrant**
- Run `logout` to logout from the environment. Then run `vagrant halt` to shutdown 
  vagrant. Or just run `vagrant halt` from another terminal.
