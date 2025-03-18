odoo.define('yudha_cool_web_login.showormasked', function (require) {
"use strict";

    var FieldChar = require('web.basic_fields').InputField;
    var TranslatableFieldMixin = require('web.basic_fields').TranslatableFieldMixin;
    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var deprecatedFields = require('web.basic_fields.deprecated');
    var dom = require('web.dom');
    var qweb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    var ShowOrMasked = FieldChar.extend(TranslatableFieldMixin, {
        description: _lt("ShowOrMasked"),
        className: 'o_field_char',
        tagName: 'span',
        supportedFieldTypes: ['char'],
        template: 'ShowOrMasked',
        events: _.extend({}, FieldChar.prototype.events, {
            'click div.input-group-append button.btn.btn-secondary': '_onShowOrMasked',
        }),
        init: function () {
            this._super.apply(this, arguments);


        },
        isSet: function () {
            return this.value === 0 || this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this.$input =this.$el.find("#showpassword");
            if (this.mode === 'edit') {
                if (this.field.translate) {
                    this.$el = this.$el.add(this._renderTranslateButton());
                    this.$el.addClass('o_field_translate');
                }
            }
            this.$input.attr('name', this.name);
            this.$input.addClass('o_field_widget');
            return this._super();
        },
        _prepareInput: function ($input) {
            this.$input = $input || $("<input/>");
            this.$input.addClass('o_input');
            var inputAttrs = { placeholder: this.attrs.placeholder || "" };
            var inputVal;
            if (this.nodeOptions.isPassword) {
                inputAttrs = _.extend(inputAttrs, { type: 'password', autocomplete: this.attrs.autocomplete || 'new-password' });
                inputVal = this.value || '';
            } else {
                inputAttrs = _.extend(inputAttrs, { type: 'text', autocomplete: this.attrs.autocomplete || 'off'});
                inputVal = this._formatValue(this.value);
            }
            this.$input.attr(inputAttrs);
            this.$input.val(inputVal);

            return this.$input;
        },

        _renderEdit: function () {
            this._super.apply(this, arguments);
            this.$input =this.$el.find("#showpassword");
            this._prepareInput(this.$input);
            if (this.field.size && this.field.size > 0) {
                this.$el.attr('maxlength', this.field.size);
            }
            if (this.field.translate) {
                this.$el = this.$el.add(this._renderTranslateButton());
                this.$el.addClass('o_field_translate');
            }
        },
        _renderReadonly: function () {
            this._super.apply(this, arguments);
            if (this.value) {
                console.log('isinya '+ this.value)
                this.$el.text('');
                this.$el.append('<input  class="o_field_char" name="" placeholder="" type="password"'+' value="'+this.value+'" autocomplete="" style="outline: none;border: none !important;"/>');
            } else {
            }
        },
        _onShowOrMasked: function (ev) {
            ev.stopPropagation();
            var icon = $(this.$el).find('i.fa.fa-eye').length
            if (icon == 1) {
                $(this.$el).find('i.fa.fa-eye').removeClass('fa-eye').addClass('fa-eye-slash');
                $(this.$el).find('input[type="password"]').prop('type', 'text');
            } else {
                $(this.$el).find('i.fa.fa-eye-slash').removeClass('fa-eye-slash').addClass('fa-eye');
                $(this.$el).find('input[type="text"]').prop('type', 'password');
            }
        },
    });
    fieldRegistry.add('show_or_masked', ShowOrMasked);
    return{
        ShowOrMasked:ShowOrMasked,
    }
});