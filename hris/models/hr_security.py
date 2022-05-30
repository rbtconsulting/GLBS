# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, SUPERUSER_ID
from lxml import etree
import json
from odoo.osv.orm import setup_modifiers

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def fields_view_get(self,view_id= None,view_type='tree',toolbar=False,submenu=False):
        res = super(ResUsers,self).fields_view_get(view_id= view_id,view_type =view_type,toolbar=toolbar,submenu =False)
        active_id = self.env.context.get('active_id',False)
        state = self.env['res.users'].browse(active_id)
        firstlevel = self.env['res.users'].has_group('hris.group_firstlevel')
        approver = self.env['res.users'].has_group('hris.group_approver')
        hr_manager = self.env['res.users'].has_group('hris.group_hr_user')
        time_keeper = self.env['res.users'].has_group('hris.group_timekeeper')
        current_user = self.env.user.groups_id.mapped('id')
        doc = etree.XML(res['arch'])

        
        ctx = self.env.context.get('form_view_ref', False)
     
        if view_type == 'tree' and not ctx:

            if firstlevel or approver or time_keeper in current_user:
                for node in doc.xpath("//tree"):
                    node.set('create','1')
                    node.set('delete', '1')
                    
        if view_type == 'form' and not ctx:
            if firstlevel or approver in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '1')
                    node.set('edit','1')
                    node.set('delete', '0')


            if hr_manager in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '1')
                    node.set('edit','1')

            if time_keeper in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '1')
                    node.set('edit', '1')
                    node.set('delete', '0')
                options = "{'no_open': True}"
                
        res['arch'] = etree.tostring(doc)
        return res
        

class ResGroups(models.Model):
    _inherit = 'res.groups'

    menu_no_access = fields.Many2many('ir.ui.menu', 'ir_ui_menu_no_group_rel', 'group_id', 'menu_id', 'No Access Menu')


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    no_groups = fields.Many2many('res.groups', 'ir_ui_menu_no_group_rel', 'menu_id', 'group_id', 'No Groups')

    @api.multi
    @api.returns('self')
    def _filter_visible_menus(self):
        menus = super(IrUiMenu, self)._filter_visible_menus()
        visible_ids = menus and menus.ids or []
        my_attendance = self.env.ref('hr_attendance.menu_hr_attendance_my_attendances').id
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if not employee:
            if my_attendance in visible_ids:
                visible_ids.remove(my_attendance)
        if self.env.user.id != SUPERUSER_ID:
            groups = self.env.user.groups_id
            menus = menus.filtered(lambda menu: not(menu.no_groups & groups))
        menus = self.browse(visible_ids)
        return menus


class HiddenAdminAccount(models.Model):
    _inherit = 'mail.channel'

    @api.model
    def hide_admin(self, uuid):
        admin_id = self.env['res.users'].sudo().browse(SUPERUSER_ID).partner_id.id
        res = super(HiddenAdminAccount,self).hide_admin(uuid)
        return[p for p in res if p.get('id') != admin_id]


class LeavesSummary(models.Model):
    _inherit = 'ir.values'

    def _drop_print_leaves_summary_menu(self,action_slot,model,res):
        if model == 'hr.employee' and action_slot == 'client_print_multi':
            leaves_summary_report = self.env.ref('hr_holidays.hr_holidays_summary_employee_value')
            group_firstlevel = self.user_has_groups('hris.group_firstlevel')
            res = [r for r in res if r[0] != leaves_summary_report.id or group_firstlevel]
        return res

    @api.model
    def get_action(self,action_slot,model,res_id = False):
        res = super(LeavesSummary,self).get_action(action_slot,model,res_id = res_id)
        res = self._drop_print_leaves_summary_menu(action_slot,model,res)
        return res


class AttendanceAccessRights(models.Model):
    _inherit = 'hr.attendance'
    
    @api.model
    def fields_view_get(self,view_id= None,view_type='tree',toolbar=False,submenu=False):
        res = super(AttendanceAccessRights,self).fields_view_get(view_id= view_id,view_type =view_type,toolbar=toolbar,submenu =False)
        active_id = self.env.context.get('active_id',False)
        state = self.env['hr.attendance'].browse(active_id)
        firstlevel = self.env['res.users'].has_group('hris.group_firstlevel')
        approver = self.env['res.users'].has_group('hris.group_approver')
        hr_manager = self.env['res.users'].has_group('hris.group_hr_user')
        time_keeper = self.env['res.users'].has_group('hris.group_timekeeper')
        current_user = self.env.user.groups_id.mapped('id')
        doc = etree.XML(res['arch'])

        
        ctx = self.env.context.get('form_view_ref', False)
     
        if view_type == 'tree' and not ctx:

            if firstlevel or approver or time_keeper in current_user:
                for node in doc.xpath("//tree"):
                    node.set('create','0')
                    node.set('delete', '0')
                    
        if view_type == 'form' and not ctx:
            if firstlevel or approver in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '0')
                    node.set('edit','0')
                    node.set('delete', '0')

                options = "{'no_open': True}"
                work_time_line_id = doc.xpath("//field[@name = 'work_time_line_id']")
                emp_id = doc.xpath("//field[@name = 'employee_id']")
                for node in work_time_line_id:
                    node.set('options', options)
                    setup_modifiers(node, res['fields']['work_time_line_id'])

                for node in emp_id:
                    node.set('options',options)
                    setup_modifiers(node,res['fields']['employee_id'])

            if hr_manager in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '1')
                    node.set('edit','1')

            if time_keeper in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '0')
                    node.set('edit', '0')
                    node.set('delete', '0')
                options = "{'no_open': True}"
                work_time_line_id = doc.xpath("//field[@name = 'work_time_line_id']")
                emp_id = doc.xpath("//field[@name = 'employee_id']")
                for node in work_time_line_id:
                    node.set('options', options)
                    setup_modifiers(node, res['fields']['work_time_line_id'])
                    
                for node in emp_id:
                    node.set('options', options)
                    setup_modifiers(node, res['fields']['work_time_line_id'])

                for node in emp_id:
                    node.set('options', options)
                    setup_modifiers(node, res['fields']['employee_id'])

        res['arch'] = etree.tostring(doc)
        return res
        

class AttendanceChangeAccess(models.Model):
    _inherit = 'hr.attendance.change'

    
    @api.model
    def fields_view_get(self,view_id= None,view_type='form',toolbar=False,submenu=False):
        res = super(AttendanceChangeAccess, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False,)
        firstlevel = self.env['res.users'].has_group('hris.group_firstlevel')
        approver = self.env['res.users'].has_group('hris.group_approver')
        time_keeper = self.env['res.users'].has_group('hris.group_timekeeper')
        current_user = self.env.user.groups_id.mapped('id')
        doc = etree.XML(res['arch'])

        
        if view_type == 'tree':
            if time_keeper in current_user:
                for node in doc.xpath("//tree"):
                    node.set('create', '0')
                    node.set('delete', '0')
                    node.set('edit', '0')
        if view_type == 'form':
            if time_keeper in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '0')
                    node.set('delete', '0')
                    node.set('edit', '0')

        if view_type == 'form':
            if firstlevel or approver in current_user:
                domain = "['|',('user_id','=',uid),('parent_id.user_id','=',uid)]"
                emp_id = doc.xpath("//field[@name='employee_id']")
            
                for node in emp_id:
                    node.set('domain', domain)
                    setup_modifiers(node, res['fields']['employee_id'])
                    node.set('domain',domain)
                    setup_modifiers(node,res['fields']['employee_id'])

        res['arch'] = etree.tostring(doc)
        return res

class AttendanceOvertimeAccess(models.Model):
    _inherit = 'hr.attendance.overtime'
    
    
    @api.model
    def fields_view_get(self,view_id= None,view_type='form',toolbar=False,submenu=False):
        res = super(AttendanceOvertimeAccess, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False,)
        firstlevel = self.env['res.users'].has_group('hris.group_firstlevel')
        approver = self.env['res.users'].has_group('hris.group_approver')
        time_keeper = self.env['res.users'].has_group('hris.group_timekeeper')
        current_user = self.env.user.groups_id.mapped('id')
        doc = etree.XML(res['arch'])

        if view_type == 'tree':
            if time_keeper  in current_user:
                for node in doc.xpath("//tree"):
                    node.set('create', '0')
                    node.set('delete', '0')
                    node.set('edit', '0')

            if approver or firstlevel in current_user:
                for node in doc.xpath("//tree"):
                    node.set('delete', '0')

        if view_type == 'form':
            for node in doc.xpath("//form"):
               node.set('duplicate', '0')
               if time_keeper in current_user:

                    node.set('create', '0')
                    node.set('delete', '0')
                    node.set('edit', '0')
            if approver or firstlevel  in current_user:
                for node in doc.xpath("//form"):
                    node.set('delete', '0')



        if view_type == 'form':

            if firstlevel or approver or time_keeper in current_user:
                domain = "['|',('user_id','=',uid),('parent_id.user_id','=',uid)]"
                emp_id = doc.xpath("//field[@name = 'employee_id']")
                for node in emp_id:
                    node.set('domain',domain)
                    setup_modifiers(node,res['fields']['employee_id'])
            else:
                domain = "[(1,'=',1)]"
                emp_id = doc.xpath("//field[@name = 'employee_id']")
                for node in emp_id:
                    node.set('domain',domain)
                    setup_modifiers(node,res['fields']['employee_id'])


        res['arch'] = etree.tostring(doc)
        return res
    
    @api.one
    def set_readonly(self):
        self.readonly_field = self.env['res.users'].has_group('hris.group_firstlevel')

    readonly_field = fields.Boolean(compute='set_readonly')

class HolidaysAccess(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def fields_view_get(self,view_id= None,view_type='form',toolbar=False,submenu=False):
        res = super(HolidaysAccess, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False,)
        firstlevel = self.env['res.users'].has_group('hris.group_firstlevel')
        approver = self.env['res.users'].has_group('hris.group_approver')
        current_user = self.env.user.groups_id.mapped('id')
        time_keeper = self.env['res.users'].has_group('hris.group_timekeeper')
        doc = etree.XML(res['arch'])
        if view_type == 'tree':
            if time_keeper in current_user:
                for node in doc.xpath("//tree"):
                    node.set('create', '0')
                    node.set('delete', '0')
                    node.set('edit', '0')

            if approver or firstlevel in current_user:
                for node in doc.xpath("//tree"):
                    node.set('delete', '0')
        if view_type == 'form':
            if time_keeper in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '0')
                    node.set('delete', '0')
                    node.set('edit', '0')
            if approver or firstlevel  in current_user:
                for node in doc.xpath("//form"):
                    node.set('delete', '0')


        res['arch'] = etree.tostring(doc)
        return res
        
class PayslipAccess(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def fields_view_get(self,view_id= None,view_type='tree',toolbar=False,submenu=False):
        res = super(PayslipAccess,self).fields_view_get(view_id= view_id,view_type =view_type,toolbar=toolbar,submenu =False)
        firstlevel = self.env['res.users'].has_group('hris.group_firstlevel')
        approver = self.env['res.users'].has_group('hris.group_approver')
        hr_manager = self.env['res.users'].has_group('hris.group_hr_user')
        current_user = self.env.user.groups_id.mapped('id')
        doc = etree.XML(res['arch'])

        if view_type == 'tree':
            if firstlevel or approver in current_user:
                for node in doc.xpath("//tree"):
                    node.set('create','0')
                    node.set('edit', '0')

        if view_type == 'form':
            for node in doc.xpath("//form"):
               node.set('duplicate', '0')
               if firstlevel or approver in current_user:

                    node.set('create', '0')
                    node.set('edit','0')


            if hr_manager in current_user:
                for node in doc.xpath("//form"):
                    node.set('create', '1')
                    node.set('edit','1')

        res['arch'] = etree.tostring(doc)
        return res
    
class HRISmanageraccess(models.Model):
    _inherit = 'hr.employee'
    
    @api.model
    def fields_view_get(self, view_id= None, view_type='tree', toolbar=False, submenu=False):
        res = super(HRISmanageraccess, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        hr_manager = self.env['res.users'].has_group('hris.group_hr_user')
        firstlevel = self.env['res.users'].has_group('hris.group_firstlevel')
        approver = self.env['res.users'].has_group('hris.group_approver')
        current_user = self.env.user.groups_id.mapped('id')
        doc = etree.XML(res['arch'])
        
        if view_type == 'form':
            if hr_manager in current_user:
                for node in doc.xpath("//form"):
                    node.set('create','1')
                    node.set('edit','1')
            if firstlevel or approver in current_user:
                for node in doc.xpath("//form"):
                    node.set('create','0')
                    node.set('edit','0')
        if view_type == 'tree':
            if hr_manager in current_user:
                for node in doc.xpath("//tree"):
                    node.set('create','1')
                    node.set('edit','1')
        if view_type == 'kanban':
            if hr_manager in current_user:
                for node in doc.xpath("//kanban"):
                    node.set('create','1')
                    node.set('edit','1')

                                
        res['arch'] = etree.tostring(doc)
        return res
