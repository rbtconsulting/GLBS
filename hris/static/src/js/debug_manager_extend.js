odoo.define('hris.DebugManagerExtend', function (require) {
"use strict";

var session = require('web.session');
var DebugManager = require('web.DebugManager');


/**
 * Disable debug mode for non-admin users
 **/

DebugManager.include({
    start: function () {
	        return $.when(
	    		this._super.apply(this, arguments)
	    		.then(function (res) {
	    			if (!session.is_superuser) {
	    	    			this.leave_debug_mode();
	    	    		}
			    }.bind(this))
			);
     	},
	});
});



