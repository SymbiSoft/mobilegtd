/**
 * @author Moe
 */
// Sets the content.
ContentPanel.prototype.append = function(control) {
    uiLogger.debug("ContentPanel.append(" + content + ")");
	
    this.contentElement.appendChild(control.rootElement);
}


// Constructor.
function TreeView(id, caption, contentProvider, foldable, expanded) {
    if (id != UI_NO_INIT_ID) {
        this.init(id, caption, contentProvider, foldable, expanded);
    }
}

// TreeView inherits from Control.
TreeView.prototype = new Control(UI_NO_INIT_ID);


// Initializer - called from constructor.
TreeView.prototype.init = function(id, caption, contentProvider, foldable, expanded){
	uiLogger.debug("ContentPanel.init(" + id + ", " + caption + ", " + content + ", " + foldable + ", " + expanded + ")");
	
	// call superclass initializer
	Control.prototype.init.call(this, id, caption);
	
	this.contentProvider = contentProvider;
}