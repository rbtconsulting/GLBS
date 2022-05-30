from odoo import fields, api, models, registry
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from odoo.tools import mute_logger
from datetime import date,datetime, timedelta
from zk import ZK, const

import re
import pytz
import logging

_logger = logging.getLogger(__name__)

class inheritHRBiometric(models.Model):
    _inherit = 'hr.biometric.connection'


    def action_make_logs(self):
        """Pull attendance logs from biometric."""
        for record in self.filtered(lambda r:r.state == 'connected'):
#             self.test_connect()
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
                _logger.info('processing %s ' % (str(attendance)))
                vals = self.prepare_logs(attendance)

                vals['bio_connect_id'] = record.id

                self.env['hr.biometric.log'].create(vals)

#             self.disconnect_dev(conn)