# INI Helper Doc
Welcome to use INI Helper!

To use it, please install package with `pip install ini-helper`

Then import it: `import ini_helper` or `from ini_helper import iniFile`

Then, open a .ini file, like this: `f = open("1.ini","r")` or `f = open("1.ini","w")`

WARNING: DO NOT OPEN FILE WITH BINARY MODE!

The .ini file Like this:

    [Config]
    name=Hello World
    value=0
The full code like this:

    from ini_helper import iniFile
    f = open("ini.ini",'r')
    ini = iniFile(file=f)
    cfgObj = ini.get("Config") # Or ini["Config"]
    
]
    