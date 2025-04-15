# About
This macro sets the properties of view objects (of objects) through regex. Regex is used for filtering of the objects based on their labels.

# Screenshots
![screenshot-1](doc/images/screenshot-1.png?raw=true "Screenshot 1")
![screenshot-2](doc/images/screenshot-2.png?raw=true "Screenshot 2")

Following properties can be set:
- Diffuse color
- Ambient color
- Specular color
- Emissive color
- Line color
- Line width
- Point color
- Point size
- Shininess
- Transparency

## Settings file
The settings file is a text file that must have an extension of **".FCStdView"**.
If a FreeCAD file is **"model.FCStd"**, the settings file must be **"model.FCStdView"**.

Each line in the settings file can be any of the following formats.

## 1: Format for importing another settings file
```
import "extra-settings.FCStdView" # Relative path
import "/x/y/z/extra-settings.FCStdView" # Absolute path
```

## 2: Format for declaring a global variable
```
cBlack, 000000
```

## 3: Format for declaring a theme variable
```
themeABC, cBlack, 000000
```

## 4: Format for declaring the regex and related parameters to apply on the objects
```
-room-|-bathroom- , ${cGray150} , 333333 , 000000 , 000000 , ${cL1} , 4 , ${cBlack} , 2 , 20 , 100 # Rooms/baths

# Regex:           -room-|-bathroom-
# DiffuseColor:    ${cGray150}
# AmbientColor:    333333
# SpecularColor:   000000
# EmissiveColor:   000000
# LineColor:       ${cL1}
# LineWidth:       4
# PointColor:      ${cBlack}
# PointSize:       2
# Shininess:       20
# Transparency:    100
# OptionalComment: # Rooms/baths
```

## An example
```
import "abc.FCStdView"           # Import colors, themes and variables from a file using a relative path.
import "def.txt"                 # The extension is not manadatory to be ".FCStdView" for other imported files.
import "/home/xyz/ghi.FCStdView" # Import using an absolute path.

# Variables in the global scope.
cBlack      , 000000
cGray150    , 969696
cLightGreen , a5ffb4
cWoodldGray , 383d3f

# Variables in the "themeSolid" theme.
themeSolid , cL1   , ${cBlack}
themeSolid , cWinL , ${cBlack}
themeSolid , cStrL , ${cBlack}

# Variables in the "themeWireframe" theme.
themeWireframe , cL1   , ${cBlack}
themeWireframe , cWinL , ${cLightGreen}
themeWireframe , cStrL , ${cWoodldGray}

.*                , ${cGray150}    , 333333 , 000000 , 000000 , ${cL1}   , 2 , 191919    , 2 , 20  , 0   # All objects
-room-|-bathroom- , ${cGray150}    , 333333 , 000000 , 000000 , ${cL1}   , 4 , ${cBlack} , 2 , 20  , 100 # Rooms/baths
-window-          , ${cLightGreen} , 333333 , ff0000 , 000000 , ${cWinL} , 2 , ${cBlack} , 2 , 100 , 50  # Windows
-stairs-          , ${cWoodldGray} , 333333 , 000000 , 000000 , ${cStrL} , 2 , ${cBlack} , 2 , 20  , 0   # Stairs
^hide-            , 000000         , 000000 , 000000 , 000000 , 000000   , 0 , 000000    , 0 , 0   , -1  # Hide objects with labels starting with "hide-"
```

## Variables
The variables must be defined in a theme or in the global scope.
If multiple themes are detected, the user is prompted to choose the theme.
It is allowed to specify no theme and define variables only in the global scope.
If only one theme is detected, it is automatically chosen.

### Referencing variables
A theme can refer to another variable in the same theme or the global scope.
A variable can refer to anther variable that is not defined yet.
"col3" can refer to "col2" and "col2" can be defined later on.
For example:
```
col0, ff0000               # A variable in the global scope

themeABC, col1,    ffffff  # A variable in a theme scope
themeABC, col3,    ${col2} # A variable referring to another variable in the same theme
themeABC, col2,    ${col1} # A variable referring to another variable in the same theme
themeABC, col-abc, ${col0} # A variable referring to another variable in global scope

themeDEF, col1, 555555     # A variable in a theme scope
themeDEF, col3, ${col2}    # A variable referring to another variable in the same theme
themeDEF, col2, ${col1}    # A variable referring to another variable in the same theme
themeDEF, col4, ${col0}    # A variable referring to another variable in global scope
themeDEF, col5, ${col-abc} # Not OK as "col-abc" is not in "themeDEF" or global scope
```

### Multiple assignments to variables
Variables retain the last assigned value.
```
colA, ffffff
colA, 000000 # "colA" retains "000000"

themeABC, col1, ffffff
themeABC, col1, 000000 # "col1" retains "000000"
```

## Comments and spaces
Comment lines start with "#".
Spaces are allowed across fields as spaces are trimmed away.
```
# This is a comment line.
themeABC, col1, ffffff # Comment at the end of a line is also OK.
themeABC    ,    col1    ,    ffffff    #    OK
```

## Order of updates
Paramaters are set based on the order of regexes in the settings file. Thus, use a more selective regex earlier.
```
.*                , ${cGray150}    , 333333 , 000000 , 000000 , ${cL1}   , 2 , 191919    , 2 , 20  ,  0   # All objects
-room-|-bathroom- , ${cGray150}    , 333333 , 000000 , 000000 , ${cL1}   , 4 , ${cBlack} , 2 , 20  ,  100 # Rooms/baths
```

**".*"** regex will update all objects including objects with names containing **"-room-"** or **"-bathroom-"**.

Later, **"-room-|-bathroom-"** regex will override the values set by **".*"** only for objects with labels containing
**"-room-"** or **"-bathroom-"**.

Using **".*"** in the very beginning is not mandatory but can be used to set all objects' views to specific values
before other regexes do the selective updates.

## Hiding objects
Set the transparency to any negative value to hide the objects.
All the other CSV parameters are ignored and not set for the objects.
To make an object visible again, rename the object's label as not to match the regex and set it to visible (manually).
This script doesn't make the objects visible automatically.
```
.*                , ${cGray150}    , 333333 , 000000 , 000000 , ${cL1}   , 2 , 191919    , 2 , 20  ,  0 # All objects
^hide-            , 000000         , 000000 , 000000 , 000000 , 000000   , 0 , 000000    , 0 , 0   , -1 # Hide objects with labels starting with "hide-"
```
