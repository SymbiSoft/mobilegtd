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
    myMenu.addItem("Fetch projects",  menuItemSelected);
    // set tab-navigation mode and show softkeys
    // (only if we are in the WRT environment)
    if (window.widget) {
        widget.setNavigationEnabled(false);
        menu.showSoftkeys();
    }
    
    uiManager = new UIManager();
    windowManager = new WindowManager(uiManager);
    
    projectsView = new ListView(null, "Edit Project");
	projectsView.menu = myMenu;
    
    nameField = new TextField(null, "Enter project name");
    projectsView.addControl(nameField);
    
    // add a button to the view
    addActionButton = new NavigationButton("Add action", null, "Add Action!");
    addActionButton.addEventListener("ActionPerformed", addActionButtonClicked);
    projectsView.addControl(addActionButton);
    
    var fetchProjectsButton = new FormButton(null, "Fetch Projects");
    fetchProjectsButton.addEventListener("ActionPerformed", fetchProjectsButtonClicked);
    
    projectsView.addControl(fetchProjectsButton);
    
    
    windowManager.open(projectsView);
}

// Callback for when menu items are selected.
function menuItemSelected(id){
    switch (id) {
        case MENU_ITEM_READ_PROJECTS:
            fetchProjectsButtonClicked(null);
            break;
    }
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


function editProject(project){
    var name = project.name;
    var projectView = new ListView(null, "Edit project");
    if (project.actions) {
        actions = project.actions;
        for (i = 0; i < project.actions.length; i++) {
			action = project.actions[i];
            var actionDescriptionControl = new TextField(null, "Action description",action.description , false);
            var contextControl = new TextField(null, "Context", action.context, false);
            projectView.addControl(actionDescriptionControl);
            projectView.addControl(contextControl);
        }
    }
    projectView.closeHandler = function(){
        var actionDescription = actionDescriptionControl.getText();
        var context = contextControl.getText();
        projectView.addControl(new ContentPanel(null, "@" + context + " " + actionDescription, "<label>Context:</label><br/>  @" + context + "<br/><label>Description:</label><br/>  " + actionDescription, true, true));
        
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



function projectsReadCompleted(event){
    var projects = event.content;
    for (i = 0; i < projects.length; i++) {
        var projectName = projects[i];
        projectsView.addControl(createProjectButton(i,projectName));
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
	projectsView.addControl(new NavigationButton(null,"Pressed key "+pressedKey,"Pressed key "+pressedKey))
}
