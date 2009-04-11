includeScript("json2.js");

///////////////////////////////////////////////////////////////////////////////
// The RestfulJsonReader class implements a simple JSON fetcher and parser.

// Constructor.
function RestfulJsonReader() {
    this.httpReq = null;
    this.callback = null;
	this.serverPath = 'http://127.0.0.1:8080/';
}

// Fetches some JSON from the specified restful URL and calls the callback when the feed
// has been fetched and parsed, or if the process results in an error.
RestfulJsonReader.prototype.fetch = function(callback,path) {
    // remember callback
    this.callback = callback;
    
    // create new XML HTTP request
    this.httpReq = new Ajax();
    
    // set callback
    var self = this;
    this.httpReq.onreadystatechange = function() { self.readyStateChanged(); };
    
    // initiate the request
    this.httpReq.open("GET", this.serverPath+path, true);
    this.httpReq.send(null);
}


RestfulJsonReader.prototype.post = function(object,path) {
    // initiate the request
	var keyValuePairs = [];
	for(var key in object) {
		keyValuePairs[keyValuePairs.length] = ""+key+"="+object[key];
	}
	
	var json = keyValuePairs.join("&");//JSON.stringify(object);
    this.httpReq = new Ajax();
    this.httpReq.open("POST", this.serverPath+path, true);
	//Send the proper header information along with the request
	this.httpReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	this.httpReq.setRequestHeader("Content-length", json.length);
	this.httpReq.setRequestHeader("Connection", "close");
    this.httpReq.send(json);
}

// Callback for ready-state change events in the XML HTTP request.
RestfulJsonReader.prototype.readyStateChanged = function() {
    // complete request?
    if (this.httpReq.readyState == 4) {
        // attempt to get response status
        var responseStatus = null;
        try {
            responseStatus = this.httpReq.status;
        } catch (noStatusException) {}
        
        // handle the response and call the registered callback
        this.callback.call(this, this.handleResponse(responseStatus, this.httpReq));
    }
}

// Handles a completed response.
RestfulJsonReader.prototype.handleResponse = function(responseStatus, req) {
    if (responseStatus == 200 && req != null) {
        
        var content = JSON.parse(req.responseText);
        
        // update was completed successfully
        return { status: "ok", content: content };
    } else {
        // update failed
        return { status: "error" };
    }
}

