# -*- coding: utf-8 -*-

import logging
import time
import odoo

from odoo import http, api, SUPERUSER_ID
from odoo.http import request
import werkzeug
from Queue import Queue
from threading import Thread, Lock
from datetime import date,datetime

_logger = logging.getLogger(__name__)

try:
    from zk import ZK
except ImportError:
    _logger.error('ZK depends on pyzk python module.')
    ZK = None
"""create attendance"""       
def check_employee(env,emp_id):
    budge = str(emp_id)
    code = budge.replace(',','')
    print code,'this is the emp codeeeeeeeeeeeeeeeeeeeeeeeeee'
    emp = env['hr.employee'].search([('barcode','=',str(code))],limit = 1)
    if emp:
        print emp.bracode
        emp.biometric_device_id
        return emp.id
    else:
        return False
    
def set_date(date):
    date = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
    new_date = date.replace(hour=23, minute=59, second=59)        
    return new_date

def set_startdate(date):
    date = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
    new_date = date.replace(hour=0, minute=0, second=59)
    return new_date

def attendance_checker_previous(emp_id,time_in,env):
        att = env['hr.attendance']
        check_prev = att.search([('employee_id','=',emp_id),('check_in','<=',str(time_in)),\
                                                                     ('check_out','=',False)])
        #print check_prev,'check previos attendance',check_prev.check_in
        
        if not check_prev:
            return {'att':'clear'}
        else:
            print check_prev.check_in
            dates = []
            for records in check_prev:
                print records.check_in  
                dates.append(records.check_in)
                records.unlink()
                max_date = set_date(max(dates))
                min_date = set_startdate(min(dates))
                print max_date,min_date
                absent = att.make_absent(emp_id,str(min_date))
                #if absent == True:
                    #for rec in emp.browse(emp_det):        
                        #print "Checking Attendance for {} for absences".format(rec.name.encode('utf-8'))
                        
                return {'att':'clear'}
            
def create_attendance(env,vals):
    print 'im in attendance'
    if vals:
        if vals.get('punch') == 0:
            time_in_out = vals.get('bio_timestamp')
            emp_id = vals.get('user_id')
            emp = check_employee(env,emp_id)
            start_date = set_startdate(time_in_out.strftime('%Y-%m-%d %H:%M:%S'))
            end_date = set_date(time_in_out.strftime('%Y-%m-%d %H:%M:%S'))
            emp_att = env['hr.attendance'].search([('employee_id','=',emp),('check_in','>=',str(start_date)),\
                                                                    ('check_in','<=',str(end_date))])
            if emp:
                if emp_att:
                    pass
                else:
                    
                    check_att = attendance_checker_previous(emp, time_in_out, env)
                    if check_att.get('att') == 'clear':
                        dt = time_in_out.strftime('%Y-%m-%d %H:%M:%S')
                        env['hr.attendance'].create({'employee_id' : emp,\
                                                'check_in' : dt,\
                                                'is_raw' : True})
                    else:
                        pass
            else:
                pass
        elif vals.get('punch') == 2 or vals.get('punch') == 1:
            print 'IM IN OUT'
            time_in_out = vals.get('bio_timestamp')
            emp_id = vals.get('user_id')
            emp = check_employee(env, emp_id)
            dt = time_in_out.strftime('%Y-%m-%d %H:%M:%S')
            if emp:
                start_date = set_startdate(time_in_out.strftime('%Y-%m-%d %H:%M:%S'))
                end_date = set_date(time_in_out.strftime('%Y-%m-%d %H:%M:%S'))
                emp_att = env['hr.attendance'].search([('employee_id','=',emp),('check_in','>=',str(start_date)),\
                                                                    ('check_in','<=',str(end_date))])
                

                if emp_att:
                    if datetime.strptime(emp_att.check_in,'%Y-%m-%d %H:%M:%S') <= datetime.strptime(dt,'%Y-%m-%d %H:%M:%S'):
                        emp_att.update({'check_out':dt})
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass

class HRBiometricDevice(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.lock = Lock()
        self.biometrics = Queue()
        self.connection_id = None
        
    def lockedstart(self):
        with self.lock:
            
            if not self.isAlive():
                self.daemon = True
                self.start()
                
    def live_capture(self):
        """Start to capture realtime biometric logs."""
        conn = None
        #Check if there is connection id 
        if self.connection_id:
            
            with api.Environment.manage():
                    
                new_cr = odoo.sql_db.db_connect(self.db).cursor()
                env = odoo.api.Environment(new_cr, SUPERUSER_ID, self.context)
                new_cr.autocommit(True)
                
                bio_conn = env['hr.biometric.connection'].browse(self.connection_id)
                
                if bio_conn.live_capture:
                    #Connect to biometrics
                    zk = ZK(bio_conn.ip_address, port=bio_conn.port, 
                            timeout=bio_conn.timeout, password=bio_conn.password, 
                            force_udp=bio_conn.force_udp, ommit_ping=bio_conn.ommit_ping)
                    
                    bio_conn.write({'remarks': 'Running...'})
                            
                    try:
                    
                        _logger.debug('Connecting to device ...')
                        conn = zk.connect()
                          
                        for attendance in conn.live_capture():
                            
                            if attendance is None:
                                
                                _logger.info('No attendance')
                            else:
				_logger.info(attendance)
                                logs = env['hr.biometric.connection'].prepare_logs(attendance)
                                logs['bio_connect_id'] = bio_conn.id
                                env['hr.biometric.log'].create(logs)
                		create_attendance(env,logs)

                                _logger.info(attendance)
                            
                            env['hr.biometric.connection'].invalidate_cache()
                            bio_conn = env['hr.biometric.connection'].browse(bio_conn.id)
                           
                            #Gracefully end live capturing of logs 
                            if not bio_conn.live_capture:
                                conn.end_live_capture = True
                                _logger.debug('Disabling live capture')
                                
                    except Exception as e:
                        _logger.error(e)
                        if not new_cr.closed:
                            _logger.debug('Closing connection')
                            new_cr.close()
                        
                    finally:
            
                        if not new_cr.closed:
                            _logger.debug('Closing connection')
                            new_cr.close()
                         
                        if conn:
                            _logger.debug('Disconnecting device..')
                            conn.disconnect()
                            
    def start_live_capture(self, connection_id, db, context):
        """Start the thread to capture realtime biometric logs."""
        self.lockedstart()
    
        self.db = db
        self.context = context
        
        self.biometrics.put((time.time(),connection_id, db))
        
    def run(self):
        while True:
            timestamp,conn,db = self.biometrics.get(True)
            
            if conn == self.connection_id:
                self.live_capture()
                _logger.debug('Still running...')
                time.sleep(5) 
                continue
            else:
                _logger.debug('Creating new connection thread.')
                self.connection_id = conn
                self.biometrics.put((timestamp ,conn, db))
                
biometric_device = None
if ZK:
    biometric_device = HRBiometricDevice()

class BiometricDriver(http.Controller):
    
    @http.route('/hris/biometric/<int:id>', type='http', auth='user', methods=['GET'], cors='*')
    def biometric(self, **kwargs):
        if 'id' in kwargs:
            biometric_conn_id = kwargs.get('id')
            domain = [
                ('id', '=', biometric_conn_id),
                ('state', '=', 'connected'),
                ('live_capture', '=', True)
                ]
            conn = http.request.env['hr.biometric.connection'].sudo().search(domain)
            db = http.request.db
            context = http.request.env.context
            #start of biometric thread
            biometric_device.start_live_capture(conn.id, db, context) if biometric_device and conn else None
            
            query = werkzeug.urls.url_encode({
                    'id': biometric_conn_id,
                    'view_type': 'form',
                    'model': 'hr.biometric.connection',
                    'menu': request.env.ref('hris.menu_biometric_connection').id,
                    'action': request.env.ref('hris.action_biometric_connection').id
                })
            
            return werkzeug.utils.redirect('/web#%s'%query)
        return ''
