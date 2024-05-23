odoo.define('tabby_payment.tabby_checkout', require => {
    'use strict';

    const core = require('web.core');
    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const _t = core._t;

    setTimeout(function(){
        $(document).ready(function(e) {
            var ajax = require('web.ajax');
            ajax.jsonRpc("/get_tabby_data", 'call', {}, {
             'async' : false
              }).then(function(data) {
                    console.log(data);
                    window.location.href = data.re_url;
              });

            });
    },1000);    
});