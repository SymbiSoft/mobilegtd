includeScript("TreeView.js");
includeScript("MenuCandidate.js");
///////////////////////////////////////////////////////////////////////////////

// Reference to the WRTKit user interface manager and main view.
var uiManager;
var projectsView;
var windowManager;

// Reference to controls in the main view.
var addActionButton;
var nameField;

//about view label control
var aboutLabel;

// Constants for menu item identifiers.
var restfulJsonReader;
var myMenu;

// Called from the onload event handler to initialize the widget.
function init(){
    restfulJsonReader = new RestfulJsonReader();
	myMenu = new MenuCandidate();
    //create about menu
    myMenu.addItem("Fetch projects",  fetchProjectsButtonClicked);
    // set tab-navigation mode and show softkeys
    // (only if we are in the WRT environment)
    if (window.widget) {
        widget.setNavigationEnabled(false);
        menu.showSoftkeys();
    }
    
    uiManager = new UIManager();
    windowManager = new WindowManager(uiManager);
    
    projectsView = new ListView(null, "Projects");
	projectsView.menu = myMenu;
    
    nameField = new TextField(null, "New project");
	nameField.addEventListener("FocusStateChanged", function(event){
		var focused = event.value;
		if (!focused && nameField.getText()!="") {
			restfulJsonReader.post({"name": nameField.getText()},"projects");
			nameField.setText("");
		}
	});
	nameField.addEventListener("ValueChanged", function(event){
		alert(event.value);
	});

    projectsView.addControl(nameField);
	fetchProjectsButtonClicked();
    
    
    windowManager.open(projectsView);
}

//Displays the About view
function showAboutView(){
    aboutLabel.setText("This Widget includes software licensed from Nokia &copy 2008");
    
    setAboutViewSoftkeys();
    uiManager.setView(aboutView);
}

// Sets the soft keys for about view.
function setAboutViewSoftkeys(){
    if (window.widget) {
        // set right soft key to "Ok" (returns to main view)
        menu.setRightSoftkeyLabel("Ok", showprojectsView);
    }
}


// Called when the addAction-button is clicked.
function addActionButtonClicked(event){
    editAction(nameField.getText());
}

function editAction(name){
    var actionView = new ListView(null, "Edit action");
    var actionDescriptionControl = new TextField(null, "Action description", "Action for " + name, false);
    var contextControl = new TextField(null, "Context", "Computer", false);
    actionView.addControl(actionDescriptionControl);
    actionView.addControl(contextControl);
    actionView.closeHandler = function(){
        var actionDescription = actionDescriptionControl.getText();
        var context = contextControl.getText();
        var contentPanel = new ContentPanel(null, "@" + context + " " + actionDescription, "", true, true);
        var subPanel = new ContentPanel(null, "@sub " + actionDescription, "", true, true);
        subPanel.append(new ContentPanel(null, "@subsub " + actionDescription, "", true, true));
        contentPanel.append(subPanel);
        projectsView.addControl(contentPanel);
        
    }
    windowManager.open(actionView);
    
}

function unorderedListHtml(list) {
	return "<ul><li>"+list.join("</li><li>")+"</li></ul>";
}

function editInfoButtonClicked(event){}

function editProject(project){
    var name = project.name;
    var projectView = new ListView(null, name);
    var nameField = new TextField(null, "Project name");
	nameField.setText(name);
	nameField.addEventListener("ValueChanged", function(event){
		var path = "projects/"+project.id;
		restfulJsonReader.post({"name":event.value},path);
	});
	projectView.addControl(nameField);
	
	for(var i in project.infos) {
		infoButton = new NavigationButton(project.infos[i], null, project.infos[i]);
		infoButton.addEventListener("ActionPerformed", editInfoButtonClicked);
		projectView.addControl(infoButton);
		
	}
	// add a button to the view
    addActionButton = new NavigationButton("Add action", null, "Add Action!");
    addActionButton.addEventListener("ActionPerformed", addActionButtonClicked);
    projectView.addControl(addActionButton);
    if (project.actions) {
		var actionsByContext = {};
        actions = project.actions;
        for (i = 0; i < project.actions.length; i++) {
			action = project.actions[i];
			if (!actionsByContext[action.context]) {
				actionsByContext[action.context]=[];
			}
			actionsByContext[action.context].push(action);
        }
		for(var context in actionsByContext) {
			var actions = actionsByContext[context];
			var actionDescriptions = [];
			for(var index in actions) {
				actionDescriptions.push(actions[index].description);
			}
			var actionList = unorderedListHtml(actionDescriptions);
	        projectView.addControl(new ContentPanel(null, "@" + context, actionList, true, true));		
		}
    }
    projectView.closeHandler = function(){
    }
    windowManager.open(projectView);
}

function editProjectButtonClicked(event){
    var project = event.content;
    editProject(project);
}


function fetchProjectsButtonClicked(event){
    restfulJsonReader.fetch(projectsReadCompleted, "projects");
}

function createProjectButton(index,projectName){
    var projectButton = new NavigationButton(null, null, projectName);
    projectButton.addEventListener("ActionPerformed", function(){
        fetchProject(index)
    });
    return projectButton;
}

function fetchProject(index){
    restfulJsonReader.fetch(editProjectButtonClicked, "projects/" + index);
}

function compareByName(first,second) {
	aa = first.name.toLowerCase();
	bb = second.name.toLowerCase();
	if (aa==bb) {
		return 0;
	}
	if (aa<bb) {
		return -1;
	}
	return 1;
}

function projectsReadCompleted(event){
    var projectNames = event.content;
	var projects = [];
	for(i in projectNames) {
		projects[i]={"name":projectNames[i],"index":i};
	}
	projects.sort(compareByName);
    for (i = 0; i < projects.length; i++) {
        var projectName = projects[i];
        projectsView.addControl(createProjectButton(projectName.index,projectName.name));
    }
}


/*
 * attach key listeners
 */
document.onkeyup = keyUp;

/*
 * disable cursor navigation - otherwise cursor
 * key events are not received by keypress callbacks
 * widget.setNavigationEnabled(false);
 */


function keyUp(event){
    var pressedKey = event.keyCode - 48;
	//projectsView.addControl(new NavigationButton(null,"Pressed key "+pressedKey,"Pressed key "+pressedKey))
}
