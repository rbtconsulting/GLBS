from odoo import fields, api, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

from zk import ZK, const

import re
import pytz
import logging

_logger = logging.getLogger(__name__)

class HRBiometric(models.Model):
    _name = 'hr.biometric.connection'
    _description = 'Biometric Connection'
    
    def connect_dev(self, record, timeout=0):
        """Return an instance of the connected device."""
        conn = None
        
        zk = ZK(record.ip_address, port=record.port,password=record.password,\
                 force_udp=record.force_udp, \
                 ommit_ping=record.ommit_ping)

        record.write({'remarks': "Connecting device..."})
        try:
            conn = zk.connect()
        except Exception as e:

            print ("Connection Failed : {}".format(e))

        finally:
            if conn is not None:
                record.write({'remarks': 'OK', 'state': 'connected'})
                record.device_name = conn.get_device_name()
                record.serial_number = conn.get_serialnumber()
                record.mac_address = conn.get_mac()
            else:
                #self.disconnect_dev(conn)
                record.write({'remarks': "Connection Failed : {}".format(e), 'state': 'disconnected'})
                record.device_name = ''
                record.serial_number = ''
                record.mac_address = ''

        return conn

    def disconnect_dev(self, record):
        """Disconnect the device."""
        if record:
            record.disconnect()
        
    def test_connect(self):
        self.connect_dev(self, timeout=0)
         
    @api.constrains('ip_address', 'port')
    def check_connection(self):
        """Validates ip address format and connection details."""
        for record in self:
            pattern = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
            
            valid = re.match(pattern, record.ip_address)
            if valid is None:
                raise ValidationError(_('IP Address is invalid'))
            
            count = self.search_count([('id', '!=', record.id), ('ip_address', '=', record.ip_address), ('port', '=', record.port)])
            if count > 0:
                raise ValidationError(_('Connection ip address and port must be unique!'))
    
    def rec_to_utc(self, to_convert):
        tz_name = self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise UserError(_(
                'No timezone!\n\nConfigure your timezone\n\nClick your Profile Name>Preferences>Timezone(Asia/Manila)'))
        local = pytz.timezone('Asia/Manila')
        local_dt_log = local.localize(to_convert, is_dst=None)
        return local_dt_log.astimezone(pytz.utc)

    def prepare_logs(self, log):
        """Prepare logs format"""
        values = {}
        values['user_id'] = log.user_id
        values['bio_timestamp'] = self.rec_to_utc(log.timestamp)
        values['status'] = log.status
        values['punch'] = log.punch
        return values
    
    def get_attendance(self, record, conn):
        """Retrieve user logs."""
        att = []
        try:
            att = conn.get_attendance()
            record.write({'remarks': ''})
        
        except Exception as e:
            record.write({'remarks': e})
        
        return att
        
    def action_live_capture(self):
        self.ensure_one()
        negate_value = self.live_capture
        self.write({'live_capture': not negate_value, 'end_live_capture': False})
        url = self.env['ir.config_parameter'].get_param('web.base.url')
        
        
        if self.live_capture:
            import requests
            import json
            headers = {'Content-Type': 'application/json'}
            data = {
            'jsonrpc':'2.0',
            'method':'call',
            'params':{'context':{},
                    'id': self.id
                    },
            }
            
            return {
            "type": "ir.actions.act_url",
            "url": url + "/hris/biometric/" + str(self.id),
            "target": "self",
            }
        return {}
    
    def action_end_live_capture(self):
        negate_value = self.end_live_capture
        return self.write({'remarks': '', 'end_live_capture': not negate_value, 'live_capture': False})
    
    def btn_live_capture(self):
        return self.action_live_capture()
        
    def btn_end_live_capture(self):
        self.action_end_live_capture()
    
    def action_make_logs(self):
        """Pull attendance logs from biometric."""
        for record in self.filtered(lambda r:r.state == 'connected'):
            self.test_connect()
            conn = self.connect_dev(record)
            for attendance in self.get_attendance(record, conn):
                domain = [
                    ('bio_connect_id', '=', record.id),
                    ('user_id', '=', attendance.user_id),
                    ('bio_timestamp', '=', fields.Datetime.to_string(self.rec_to_utc(attendance.timestamp))),
                    ('status', '=', attendance.status),
                    ('punch', '=', attendance.punch)
                    ]
                
                count = self.env['hr.biometric.log'].search_count(domain)
                if count > 0:
                    continue
                
                vals = self.prepare_logs(attendance)
                vals['bio_connect_id'] = record.id
                
                if conn:
                
                    record.device_name = conn.get_device_name()
                    record.serial_number = conn.get_serialnumber()
                    record.mac_address = conn.get_mac()
                
                else:
                    record.device_name = ''
                    record.serial_number = ''
                    record.mac_address = ''
                
                self.env['hr.biometric.log'].create(vals)
            
            self.disconnect_dev(conn)

    def _cron_get_attendance(self):
        for rec in self.search([]):
            rec.btn_get_attendance()

    def btn_get_attendance(self):
        self.action_make_logs()
        
    def action_connect(self):
        self.test_connect()
    
    def action_disconnect(self):
        return self.write({'remarks':'','state': 'disconnected', 'live_capture':False, 'end_live_capture':False,
                           'device_name': '', 'serial_number': '', 'mac_address': ''})
    
    def btn_connect(self):
        self.action_connect()
    
    def btn_disconnect(self):
        self.action_disconnect()
        
    @api.depends('state')
    def _get_device_information(self):
        """Get device information of the connected device."""
        for record in self.filtered(lambda r:r.state == 'connected'):
            conn = self.connect_dev(record, timeout=0)
            
            if conn:
                
                record.device_name = conn.get_device_name()
                record.serial_number = conn.get_serialnumber()
                record.mac_address = conn.get_mac()
            
            else:
                record.device_name = ''
                record.serial_number = ''
                record.mac_address = ''
                
    name = fields.Char('Connection Name', required=True)
    ip_address = fields.Char('IP Address', required=True)
    port = fields.Integer('Port', required=True, default=4370)
    timeout = fields.Integer('Timeout', default=5)
    password = fields.Char('Password')
    force_udp = fields.Boolean('Force UDP')
    ommit_ping = fields.Boolean('Ommit Ping')
    verbose = fields.Boolean('Verbose')
    
    device_name = fields.Char('Device Name', store=True)
    serial_number = fields.Char('Serial Number', store=True)
    mac_address = fields.Char('MAC Address', store=True)
    state = fields.Selection([('connected', 'Connected'),
                              ('disconnected', 'Disconnected')], default='disconnected')
    
    live_capture = fields.Boolean('Live Capture', help="Enable real-time capturing of attendance logs")
    end_live_capture = fields.Boolean('End Live Capture', help='Disable real-time capturing of attendance log')
    
    biometric_logs = fields.One2many('hr.biometric.log', 'bio_connect_id', 'Biometric Logs')
    remarks = fields.Text('Remarks')

class HRBiometricLogs(models.Model):
    _name = 'hr.biometric.log'
    _description = 'HR Biometric Log'
    _order = 'bio_timestamp desc'
    
    bio_connect_id = fields.Many2one('hr.biometric.connection', 'Connection')
    user_id = fields.Integer('User ID')
    bio_timestamp = fields.Datetime('Timestamp')
    status = fields.Integer('Status')
    punch = fields.Integer('Punch')
    log_processed = fields.Boolean(default=False)
    
    
    
