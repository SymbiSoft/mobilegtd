function WindowManager(uiManager) {
    this.init(uiManager);
}

// Initializer - called from constructor.
WindowManager.prototype.init = function(uiManager) {
    this.uiManager = uiManager;
}

WindowManager.prototype.open = function(view) {
    this.previousView = this.uiManager.getView();
//	this.previousRightSoftkeyLabel = menu.get
	this.view = view;
	this.uiManager.setView(view);
	var obj = this;
	if(view.menu) {
		view.menu.activate();
	}
	if (this.previousView == null) {
		menu.setRightSoftkeyLabel("Exit", function(){
		});		
	}
	else {
		menu.setRightSoftkeyLabel("Back", function(){
			close(obj)
		});
	}
}

close = function(obj) {
	    
    // set right softkey to "exit"
    if (window.widget) {
        menu.setRightSoftkeyLabel("", null);
    }
	if(obj.view.closeHandler) 
		obj.view.closeHandler();
    obj.uiManager.setView(obj.previousView);
}

