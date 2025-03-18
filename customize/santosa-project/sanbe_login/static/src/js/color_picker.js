odoo.define('yudha_cool_web_login.color_picker', function (require) {
"use strict";

require('web.dom_ready');
var core = require('web.core');
var config = require('web.config');

var rpc = require('web.rpc');
var session = require('web.session');

var dom = require('web.dom');
var WebClient = require('web.WebClient');
var field_registry = require('web.field_registry');
var relational_fields = require('web.relational_fields');
var FieldRadio = field_registry.get('radio');

var _t = core._t;
var qweb = core.qweb;

var FieldChar = field_registry.get('char');
var FieldColorPicker = FieldChar.extend({
    template: 'FieldColorPicker',
    widget_class: 'oe_form_field_color',
    _renderReadonly: function () {
        var show_value = this._formatValue(this.value);
        this.$el.text(show_value);
        this.$el.css("background-color", show_value);
    },
    _getValue: function () {
        var $input = this.$el.find('input');
        return $input.val();
    },
    _renderEdit: function () {
        var show_value = this.value ;
        var $input = this.$el.find('input');
        $input.val(show_value);
        this.$el.colorpicker({format: 'rgba'});
        this.$input = $input;
    }
});
field_registry.add('colorpicker', FieldColorPicker);
});