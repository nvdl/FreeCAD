# About
This macro acts as a scripts' manager.                               
Scripts should be placed in a directory named "scripts".             
This script and the "scripts" directory should be in the same parent 
directory.                                                           
Each custom script needs its own directory containing the main       
script named "custom_script.py".                                     
                                                                     
The main script, "custom_script.py", should contain a class as       
below:                                                               
                                                                     
```
class CustomScript():                                                
    def __init__(self, parent, modulePath) -> None:                  
        self.parent = parent                                         
        self.modulePath = modulePath                                 
    def run(self) -> None:                                           
        // Code to run.                                              
    def about(self) -> str:                                          
        // Helpful information about the script.                     
```

# Screenshots
![screenshot-1](doc/images/screenshot-1.png?raw=true "Screenshot 1")

# Installation
Please refer to the official guide for installation of the macro:

https://wiki.freecad.org/How_to_install_macros
