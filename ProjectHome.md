# A free GTD (Getting Things Done) application for mobile phones (Series 60) #
**MobileGTD turns your Series 60 phone into a GTD notebook on steroids**

# NEWS #
## IRC Channel ##
We have an IRC channel now! It's called #mobilegtd (irc.freenode.net).
Come over and be productive ;)

## MobileGTD be sexy! ##

I am currently thinking about giving MobileGTD a new flash lite based user interface. I have done a major rework on the back-end, so new features will be easier to implement here. But we also need a nice UI for all of this! David Allen said something like: Buy the yourself a really good pencil then you will be more likely to write things down with it.
And MobileGTD definitely needs work on this end.

## Get involved! ##
I challenge all users of MobileGTD to think about how a nice UI for MobileGTD would look like. Send me whatever comes to your mind in the form of sketches, pictures, mockups. Maybe someone even knows some flash lite?
I am really looking forward to seeing your ideas!!







# What are the features? #
  * Based on a simple file and directory structure (easy synchronization with PC)
  * Use your favourite file explorer to browse your actions
  * Usable as a simple inbox, allowing you to create projects on the fly
  * Searchable project list view
  * Project editing functionality (add/remove actions/infos)
  * Processing functionality (automatically find done actions)
  * Review assistance (find projects with no active next action and projects that have not changed for a certain time)
  * Compatible to GTDFiles
# Show me something! #
## Ok, have a look at the brand new screencast ##
[Screencast](http://mobilegtd.googlecode.com/svn/trunk/MobileGTDDocumentation/MobileGTD.htm)
## Or some screenshots ##
Click on the images to see the original Flickr page with explanations.
### The project list view ###
[http://farm2.static.flickr.com/1029/1279030251\_d8061098e8.jpg?v=0](http://www.flickr.com/photos/12505600@N08/1279030251/)
### The project details view ###
[http://farm2.static.flickr.com/1268/1279030509\_e40f76bf5c.jpg?v=0](http://www.flickr.com/photos/12505600@N08/1279030509/)
### Creating a new action ###
[http://farm2.static.flickr.com/1094/1279141203\_70f84a8c60.jpg?v=0](http://www.flickr.com/photos/12505600@N08/1279141203/)

# How does it work? #

MobileGTD uses simple text files for projects. Each line in a project file can be either an action or an info.
When adding an action to a project, a new line is added to the project file and a file is created in  a directory structure corresponding to your contexts.
If you e.g. create an action "Computer Download new version of MobileGTD" MobileGTD will create a file "Download new version of MobileGTD.act" in a directory called "Computer/".
You can also use nested contexts, e.g. "Computer/Online/" to further structur your contexts. To avoid too much typing you can define abbreviations for contexts, you could e.g. define "26" to be expanded to "Computer/Online/".

You can then use any file explorer to browse through your actions and delete done ones.
When processing projects MobileGTD automatically searches for deleted actions and sets them to done in the project file.


# How do I install and use it? #
For installation instructions see [Installation](Installation.md).
For an explanation of how to use MobileGTD I am planning to make a video,
but I'm not sure when I will have the time...

# Summary #
If this sounds rather complicated, fear not!
It's dead simple!
All you have to do is use the graphical interface to create and manage your projects and any file explorer to browse through the actions and delete the ones you have done.

# Donate #
If you like MobileGTD and it helps you in Getting Things Done you may also consider making a [donation](https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=Martin%2eMauch%40gmail%2ecom&item_name=MobileGTD&no_shipping=0&no_note=1&tax=0&currency_code=EUR&lc=US&bn=PP%2dDonationsBF&charset=UTF%2d8). This is a motivational thing, so don't ruin yourself financially ;)