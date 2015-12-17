# Setting up the configuration #
## Configuring the path of your GTD data ##
After installing the MobileGTD and the MobileGTDData package you have a GTD directory `C:\Data\GTD`. If you want to change this move the directory somewhere else and update the main configuration file `C:\system\data\mobile_gtd.cfg`
## Configuring abbreviations for contexts ##
In your GTD directory there is a configuration file called `abbreviations.cfg`. Edit it to define abbreviations for contexts. When entering actions you can use those abbreviations. Remember to put a slash at the end of each context path.
## Key shortcuts and menu entries ##
In your GTD directory there are two configuration files called `actions.cfg` and `projects.cfg`.
Each one contains several lines in the following format:
```
function_name:key_shortcut, String for menu entry
```
You can change the key shortcuts and the menu strings but you **must** keep the function names.
## Screen Layout ##
You can define screen layouts in `C:\system\data\mobile_gtd.cfg`. Possible values are 'normal', 'large' and 'full'.
## Review Configuration ##
With `inactivity_threshold` in `C:\system\data\mobile_gtd.cfg` you can define after how many days a stalled project should be scheduled for review.