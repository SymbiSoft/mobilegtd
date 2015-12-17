# 0.9.5 #
  * Automatically creates and updates configuration files
  * Active actions are set to inactive for stalling projects
  * Fixed bug where the project details view was not updated when an info was changed
  * Fixed bug where projects already set to done/tickled/someday would be scheduled for review when processing all projects

# 0.9.0 #
  * Added function to schedule projects for review that have had no activity for a certain time
  * Fixed bug with context names containing unicode letters
  * Cleaned up unicode handling
  * Added ability to add infos at the position below the cursor
  * Changing the context of an action now moves it to the context and sets the action to processed
  * Added inactive actions to initial view in Project Detail View
  * Added warning if part of the configuration is missing
# 0.8.5 #
  * Added filter functionality for projects
  * Added function to set project status
  * Added function to rename projects
  * Reads tickled and someday folders as well (hidden by default)
  * Delete key moves projects to @Done folder