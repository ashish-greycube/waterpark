frappe.ui.form.on('Customer', {
    refresh: function (frm) {
        if (frm.doc.custom_offer_message_status == "Not Sent" || frm.doc.custom_offer_message_status == undefined) {
            frm.add_custom_button(__('Send Customer Offer Message'), function () {
                frm.set_value('custom_offer_message_status', 'Sent');
                frm.set_value('custom_whatsapp_confirmation_sent', 1);
                frm.save()
            });
        }
    }
})