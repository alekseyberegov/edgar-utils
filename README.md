# Utils for EDGAR filings
```

  ______    _                    _    _ _   _ _     
 |  ____|  | |                  | |  | | | (_) |    
 | |__   __| | __ _  __ _ _ __  | |  | | |_ _| |___ 
 |  __| / _` |/ _` |/ _` | '__| | |  | | __| | / __|
 | |___| (_| | (_| | (_| | |    | |__| | |_| | \__ \
 |______\__,_|\__, |\__,_|_|     \____/ \__|_|_|___/
               __/ |                                
              |___/                                 
```

## Setting up DEV environment
* Creating Python venv
  ```
  $ python3 -m venv venv
  ```
* Activating env
  ```
  $ source ./venv/bin/activate
  ```
* Enabling PyTest in VCS. The following parameter should be set to TRUE
  ```
    python.testing.pyTestEnabled 
  ```