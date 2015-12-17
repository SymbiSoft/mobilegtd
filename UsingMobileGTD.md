It's best to read the following having your phone at hand and MobileGTD installed. After or while reading create some example projects and play around a little. I think the application is quite intuitive.
# The whole picture #
MobileGTD supports you in processing and reviewing your projects, for browsing your actions you use any file explorer you like.
## How it works ##
MobileGTD operates on a certain file and directory structure. After installing MobileGTDData you have the basic structure setup under `C:\Data\GTD`. For each project MobileGTD puts a simple text file into the subdirectory `@Projects`. Each line in a project file can be either an action or an info. When adding an action to a project, a new line is added to the project file and a file is created in a subdirectory named after the actions context. If you e.g. create an action `Computer Download new version of MobileGTD` MobileGTD will create a file `Download new version of MobileGTD.act` in a directory called `Computer/`. You can also use nested contexts, e.g. `Computer/Online/` to further structur your contexts. To avoid too much typing you can define abbreviations for contexts, you could e.g. define `26` to be expanded to `Computer/Online/`.

You can then use any file explorer to browse through your actions and delete done ones. When having MobileGTD process your projects it automatically searches for deleted actions and sets them to done in the project file.
### Example file and directory structure ###
```
C:\Data\GTD\
C:\Data\GTD\@Projects\
C:\Data\GTD\@Projects\Publish MobileGTD.prj
C:\Data\GTD\@Projects\@Review\Example project without any active actions.prj
C:\Data\GTD\@Projects\@Someday\Example project which I might do in 2 years.prj
C:\Data\GTD\@Projects\@Tickled\10 October\Week 1\Meet with Adam.prj
C:\Data\GTD\@Projects\@Done\Done project.prj
C:\Data\GTD\Computer\Online\MobileGTD\Write UsingMobileGTD Wiki page.act
C:\Data\GTD\Agenda\Joe\Can he try MobileGTD 2nd edition on his 6680.act
C:\Data\GTD\WaitingFor\Adam\Does he have a S60 2nd edition phone.act
```



# Things concerning the entire application #
All operations for which I wrote key shortcuts can be performed from the menu as well. There you also have the key shortcuts in square brackets so you don't have to remember them. You can also change them to your liking by editing projects.cfg and actions.cfg (see [PostInstallation](PostInstallation.md)).
# Projects View #
## Navigating ##
You can navigate your project list by using your cursor buttons. Alternatively you can search for projects by pressing `0` and entering one of the contained words.
## Creating a new project ##
To create a new project choose the `New Project` entry in the project list. You can always get there quickly by pressing `0` and then your select key (usually in the center of your cursor buttons). Press the select key again to create the project. MobileGTD will ask for a project name (can be changed starting with 0.8.5) and insert the new project at the start of the list.
## Filtering ##
By default MobileGTD shows you only active projects and projects scheduled for review. To toggle that filter and show show inactive projects as well simply press `1`.
## Creating a single action ##
To create a single action choose the `No Project` entry. You should use this with caution, almost all actions belong to a project that you might not have discovered yet (even writing a mail usually involves waiting for a response).
MobileGTD will ask for the project string, which is described a little down this page.
## Processing projects ##
You can use `5` to process a single project and `6` to process all projects. When processing projects MobileGTD searches for deleted action files and marks their corresponding entries in the project file as `done`. All projects for which no active actions exist will be marked as `Review`. In the project list view these projects have a `!` in front of their name.
## Changing project status ##
You can change a projects status by pressing `7`. At the moment the sequence of states is (though I might change it or make it configurable):

Processed ('') -> Review ('!') -> Tickled ('/') -> Someday ('~') -> Processed

The sign inside the braces will get displayed in front of the project name.

You can also press `8` to set a projects status to processed (unluckily called `Unreview` at the moment).
## Setting projects to done ##
You can set projects to `done` ('+') by pressing the delete key. Done projects will not be listed in any filter so if you have accidentally set a project to done you have to move it from the `@Done` folder back to your projects folder.



# Project Details View #
Careful: Projects are saved only when you exit the project details view. Be sure not to exit the application incidentally by pressing the Hang-Up button before exiting the project details view.
## Adding an info ##
To add an info simply press `4` and type the info you want to add. This can be used for desired outcomes and auxiliary information.
## Adding an action ##
To add an action press `2`. MobileGTD will ask for the action string.
### Action strings ###
An action string looks like this:
```
Context Description (Info)
```


**Context** is the place or occasion where you can do the action, e.g. `Computer`,`Home`,`Errands`...
Contexts can be nested so you can e.g. use `Errands/Walmart`.
You can also define and use abbreviations for contexts (see [PostInstallation](PostInstallation.md)).
One abbreviation I have defined for example is `26` which gets expanded to `Computer/Online` or `266` which gets expanded to `Computer/Online/Mail` (I tried to find context names that enable me to do a 1-to-1 mapping from the first letter of the context to its key on the phone).
You can also write `266Joe` which would get expanded to `Computer/Online/Mail/Joe`. Notice that I did not put a space between the numbers and the word following it. This tells MobileGTD to interpret `Joe` as part of the context. This is quite handy for the mail and agenda contexts.

**Warning:** Do not use `?` or other signs that cannot be used in file names.


The **Description** is what you will read when browing your action files. It should be something like `Imagine myself as being a black-belt GTD user`. It usually starts with or contains a verb, but some contexts are so self-defining that I do not use a verb (e.g. for mail or agenda actions I would just write what I want to say to or ask the person).
**Warning:** Do not use `?`, `/` or other signs that cannot be used in file names.


**Info** is the place where you can put informations specific to that action e.g. the telephone number of the person you want to call. This information does not get displayed in the project details view (though I might implement that one day).
## Changing action status ##
You can change the status of actions by pressing `7`. At the moment the sequence of states is (though I might change it or make it configurable):

Active ('-') -> Inactive/Later ('!') -> Done ('+') -> Active

Active is the only status in which a corresponding action file exists. When you change an active actions status to Inactive or Done the action file will be removed.