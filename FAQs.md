# Can I configure MobileGTD so that SMS messages do not show up? #

Yes, starting from version 0.9.5 you can.
The reason for including the SMS messages in the project list is that often there is an action or project resulting from a message. For this, you can open an SMS in MobileGTD and then use "Options" -> "Create new project". The text of the message will be copied to the project's infos.
I move all processed messages to custom folders "Reference" or "Done", so my SMS inbox - like my EMail inbox - is empty.
But nonetheless, here is how you can change this.
## Version 0.9.5 ##
Edit the main configuration file (usually at c:\system\data\mobile\_gtd.cfg) and set read\_sms:0
## Version 1.0 ##
In MobileGTD choose "Options" -> "Edit global configuration" and set read\_sms to 0.