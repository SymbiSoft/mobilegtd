function WindowManager(uiManager) {
    this.init(uiManager);
}

// Initializer - called from constructor.
WindowManager.prototype.init = function(uiManager) {
    this.uiManager = uiManager;
	this.viewStack = [];
}

WindowManager.prototype.open = function(view) {
	var previousView = this.uiManager.getView();
	if(previousView)
	    this.viewStack.push(previousView);
//	this.previousRightSoftkeyLabel = menu.get
	this.view = view;
	this.uiManager.setView(view);
	var obj = this;
	if(view.menu) {
		view.menu.activate();
	}
	this.setRightKey(obj);
}

WindowManager.prototype.setRightKey = function(obj) {
    if (window.widget) {
		if (obj.viewStack.length == 0) {
			menu.setRightSoftkeyLabel("Exit", function(){
			});
		}
		else {
			menu.setRightSoftkeyLabel("Back", function(){
				close(obj)
			});
		}
	}
}

close = function(obj) {
	    
	if(obj.view.closeHandler) 
		obj.view.closeHandler();
	var previousView = obj.viewStack.pop();
	obj.view = previousView;
	obj.setRightKey(obj);
    obj.uiManager.setView(previousView);
}

