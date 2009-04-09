/**
 * @author Moe
 */
function MenuCandidate() {
    this.init();
}

// Initializer - called from constructor.
MenuCandidate.prototype.init = function() {
    this.items = [];
}

MenuCandidate.prototype.addItem = function(name,callback) {
	item = new MenuItem(name,this.items.length);
	item.onSelect = callback;
	this.items.push(item);
}

MenuCandidate.prototype.activate = function() {
	menu.clear();
	for(var i=0; i <= this.items.length; i++) {
		menu.append(this.items[i]);
	}
}
