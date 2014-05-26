Ext.define('Ext.m3.Button', {
    extend: 'Ext.Button',
    xtype: 'm3-button',

    bubbleEvents: [
        'gethandler'
    ],

    initComponent: function () {
        this.callParent();

        if (typeof this.handler === 'string') {
            this.fireEvent('gethandler', this, this.handler);
        }
    }
});