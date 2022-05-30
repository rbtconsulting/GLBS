odoo.define('hris.EditFormButton', function (require) {
"use strict";

var core = require('web.core');
var FormView = require('web.FormView');
var _t = core._t;
var QWeb = core.qweb;
var Session = require('web.session');
var Model = require('web.Model');



FormView.include({
	load_record: function(record) {this._super.apply(this, arguments);
    if (this.model=='hr.holidays' && Session.uid != 1){
            if (this.get_fields_values().state == 'draft' ){
                this.$buttons.find('.o_form_button_edit').css({"display":""});
            }
            else{
                this.$buttons.find('.o_form_button_edit').css({"display":"none"});
            }
        }

	}

});

});


