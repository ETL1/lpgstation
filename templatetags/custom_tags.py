import ast
import json
import os

from typing import final
from uuid import uuid4
from django import template
import string
import base64
from random import *
import datetime
# from login.models import Access_Rights, CustomUser, User_Access_Rights
from django.db.models import Q
from django.shortcuts import render
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Sum

from core.models import Container, Item, Product, Refill
from login.models import CustomUser

register = template.Library()

def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')
 
@register.simple_tag
def get_file_size(file_path):
    file_x = file_path[1 : : ]
    rawsize = os.path.getsize(file_x)
    size = sizeof_fmt(rawsize)
    return size

@register.simple_tag
def fundaresp(strText):
    _sr = str(strText)
    return _sr

@register.simple_tag
def pageName(strText):
    _sr = str(strText)
    return fundaresp(_sr)

###########################################
#//////  Doctor/Patient Counts  //////////
###########################################

# @register.simple_tag
# def get_count_pat():
#     patient = Business_Info.objects.all().count()
#     return str(patient)

# @register.simple_tag
# def get_count_appr():
#     patient = License_Info.objects.filter(status=1).count()
#     return str(patient)

# @register.simple_tag
# def get_count_doc():
#     doctors = License_Info.objects.filter(status=3).count()
#     return str(doctors)

# @register.simple_tag
# def get_count_doc_unav():
#     doctors = License_Info.objects.filter(~Q(status=1)).count()
#     return str(doctors)

# @register.simple_tag
# def get_count_doc_av():
#     doctors = License_Info.objects.filter(status=1).count()
#     return str(doctors)

# @register.simple_tag
# def get_compliance(owner):
#     empls = License_Info.objects.filter(bus_name=owner)
#     current_year = datetime.datetime.now().year
#     for emp in empls:
#         if current_year != emp.year_end:
#             res_ = f"Non-Compliant {current_year} - {emp.year_end}"
#         else:
#             res_ = f"Compliant {current_year} - {emp.year_end}"
#         return res_
#     return res_

#///////////////////////////////////////////////

@register.simple_tag
def get_user_name(owner):
    usr = CustomUser.objects.filter(uid=owner).first()
    sr_ = f'{usr.fname} {usr.sname}'
    return str(sr_)

@register.simple_tag
def b64_encode(tage):
    encoded = base64.b64encode(bytes(tage, 'utf-8'))
    return encoded

@register.simple_tag
def b64_decode(tage):
    # decoded = base64.b64decode(bytes(tage, 'utf-8'))
    decoded = base64.b64decode(tage).decode('UTF-8')
    return decoded

@register.simple_tag
def generate_mib():
    min_char = 12
    max_char = 21
    allchar = string.ascii_letters + string.digits
    uid = ''.join(choice(allchar) for x in range(randint(min_char, max_char)))
    return uid


@register.simple_tag
def generate_dates():
    # Get the current year
    current_year = datetime.datetime.now().year
    # Generate a list of years from 1900 to the current year
    years = list(range(1900, current_year + 1))
    # Reverse the list to have the most recent year first
    years.reverse()
    # Generate HTML options for each year
    options = ""
    for year in years:
        options += f'<option value="{year}">{year}</option>\n'
        
@register.simple_tag
def get_quarter(month):
    """
    Returns the quarter of the year for a given month.
    
    Parameters:
    month (int): The month as an integer (1 for January, 2 for February, ..., 12 for December)
    
    Returns:
    int: The quarter (1, 2, 3, or 4)
    """
    if not 1 <= month <= 12:
        raise ValueError("Month must be an integer between 1 and 12")
    
    if month in [1, 2, 3]:
        return '1st'
        
    elif month in [4, 5, 6]:
        return '2nd'
        
    elif month in [7, 8, 9]:
        return '3rd'
        
    elif month in [10, 11, 12]:
        return '4th'
    

@register.simple_tag
def add_one_year(date_str):
    """
    Returns the date exactly one year from the given date.
    
    Parameters:
    date_str (str): The date as a string in the format 'YYYY-MM-DD'
    
    Returns:
    str: The new date as a string in the format 'YYYY-MM-DD'
    """
    print(date_str)
    original_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    try:
        new_date = original_date.replace(year=original_date.year + 1)
    except ValueError:
        # This handles the case where the date is February 29
        new_date = original_date + (datetime.datetime(original_date.year + 1, 3, 1) - datetime.datetime(original_date.year, 3, 1))
    
    return new_date.strftime('%Y-%m-%d')

@register.simple_tag
def add_three_months(date_str):
    """
    Returns the date exactly three months from the given date.
    
    Parameters:
    date_str (str): The date as a string in the format 'YYYY-MM-DD'
    
    Returns:
    str: The new date as a string in the format 'YYYY-MM-DD'
    """
    print(date_str)
    original_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    new_date = original_date + relativedelta(months=3)
    
    return new_date.strftime('%Y-%m-%d')

@register.simple_tag
def add_six_months(date_str):
    """
    Returns the date exactly three months from the given date.
    
    Parameters:
    date_str (str): The date as a string in the format 'YYYY-MM-DD'
    
    Returns:
    str: The new date as a string in the format 'YYYY-MM-DD'
    """
    print(date_str)
    original_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    new_date = original_date + relativedelta(months=6)
    
    return new_date.strftime('%Y-%m-%d')

@register.simple_tag
def add_one_month(date_str):
    """
    Returns the date exactly three months from the given date.
    
    Parameters:
    date_str (str): The date as a string in the format 'YYYY-MM-DD'
    
    Returns:
    str: The new date as a string in the format 'YYYY-MM-DD'
    """
    print(date_str)
    original_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    new_date = original_date + relativedelta(months=1)
    
    return new_date.strftime('%Y-%m-%d')


@register.simple_tag
def remaining_quantity(cylinder):
    return f"{cylinder.remaining_quantity()} kg"


@register.simple_tag
def get_item_name(owner):
    usr = Product.objects.filter(item_id=owner).first()
    return str(usr.name)

@register.simple_tag
def get_site_name(owner):
    try:
        usr = Container.objects.filter(id=owner).first()
        if usr is None:
            return 'Site Not Found'
        else:
            return str(usr.name)
    except:
        return "Not Assigned"
    

@register.simple_tag
def get_sku(owner):
    usr = Product.objects.filter(item_id=owner).first()
    return str(usr.sku)

@register.simple_tag
def get_unit_price(owner):
    usr = Product.objects.filter(item_id=owner).first()
    return str(usr.unit_price)

@register.simple_tag
def get_stock(owner):
    usr = Product.objects.filter(item_id=owner).first()
    return str(usr.stock)


@register.simple_tag
def get_total_price(rate):
    _value = 45
    _value *= (int(rate))
                # print(c.rate)
    return format(_value, ",")


@register.simple_tag
def get_refill_count(pk):
    inactivecount = Refill.objects.filter(qrcode=pk).count()
    return format(inactivecount, ",")

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""

@register.simple_tag
def cylinder_dispense_sales(pk):
    from django.db.models import F, Sum, DecimalField, ExpressionWrapper
    refills = Refill.objects.filter(qrcode=pk).order_by('-created_at')
    # compute (quantity_kg * 45) per row
    total_price = (
        refills.annotate(
            line_total=ExpressionWrapper(
                F("quantity_kg") * 45,   # or F("item__base_price")
                output_field=DecimalField()
            )
        ).aggregate(total=Sum("line_total"))["total"] or 0
    )
    
    return total_price
# @register.simple_tag
# def get_bus_tpin(owner):
#     usr = Business_Info.objects.filter(eid=owner).first()
#     return str(usr.tpin)

# @register.simple_tag
# def get_bus_phone(owner):
#     usr = Business_Info.objects.filter(eid=owner).first()
#     return str(usr.phone_num)

# @register.simple_tag
# def get_lic_station(owner):
#     usr = MappingClass.objects.filter(did=owner).first()
#     return str(usr.station)

# @register.simple_tag
# def get_lic_district(owner):
#     usr = MappingClass.objects.filter(did=owner).first()
#     return str(usr.district)

# @register.simple_tag
# def get_lic_province(owner):
#     usr = MappingClass.objects.filter(did=owner).first()
#     return str(usr.province)

# @register.simple_tag
# def get_bus_reg(owner):
#     usr = Business_Info.objects.filter(eid=owner).first()
#     return str(usr.add_date)

# @register.simple_tag
# def get_license_name(owner):
#     usr = Catez.objects.filter(cid=owner).first()
#     if usr == None:
#         _sr = ''
#     else:
#         _sr = usr.cat_name
#     return str(_sr)

# @register.simple_tag
# def get_license_price(licId):
#     usr = Catez.objects.filter(cid=licId)
#     _price = 0
#     for u in usr:
#         _price += (int(u.rate))
#     return format(_price, ",")

# @register.simple_tag
# def get_active_count():
#     activecount = License_Info.objects.filter(Q(status=2) | Q(status=4)).count()
#     return format(activecount, ",")

# @register.simple_tag
# def get_inactive_count():
#     inactivecount = License_Info.objects.filter(status=0).count()
#     return format(inactivecount, ",")

# @register.simple_tag
# def get_license_count():
#     inactivecount = License_Info.objects.filter(status=0).count()
#     return format(inactivecount, ",")

# @register.simple_tag
# def get_pending_count():
#     inactivecount = License_Info.objects.filter(status=0).count()
#     return format(inactivecount, ",")

# @register.simple_tag
# def get_paid_total():
#     _cate = Catez.objects.all()
#     _notices = License_Info.objects.filter(Q(status=2) | Q(status=4) | Q(status=0) & Q(pay_status=1))
#     _value = 0
#     for n in _notices:
#         for c in _cate:
#             if c.cid == n.license_type:
#                 _value += (int(c.rate))
#                 # print(c.rate)
#     return format(_value, ",")


# @register.simple_tag
# def get_unpaid_total():
#     _cate = Catez.objects.all()
#     _notices = License_Info.objects.filter(Q(status=0) & Q(pay_status=0))
#     _value = 0
#     # for n in _notices:
#     #     for c in _cate:
#     #         _value += (int(c.rate))
#     for n in _notices:
#         for c in _cate:
#             if c.cid == n.license_type:
#                 _value += (int(c.rate))
#                 # print(c.rate)
    
#     return format(_value, ",")


# @register.simple_tag
# def calculate_percentage():
#     try:
#         # Count the items with status = 0, 1, and 2
#         count0 = License_Info.objects.filter(status=0).count()
#         count1 = License_Info.objects.filter(status=1).count()
#         count2 = License_Info.objects.filter(status=2).count()

#         # Calculate the total count of items with status = 0, 1, and 2
#         total_count = count0 + count1 + count2

#         if total_count == 0:
#             return 0.0  # Avoid division by zero

#         # Calculate the percentage of items with status = 0 and 1
#         percentage = ((count0 + count1) / total_count) * 100

#         # Round to 1 decimal place
#         return round(percentage, 1)

#     except Exception as e:
#         print(f"Error: {e}")
#         return 0.0  # Return 0 or handle the error as needed
    
# @register.simple_tag
# def calculate_percentage_bus(id):
#     try:
#         # Count the items with status = 0, 1, and 2
#         count0 = License_Info.objects.filter(Q(status=0) & Q(pay_status=1)).filter(bus_name=id).count()
#         count1 = License_Info.objects.filter(Q(status=1) & Q(pay_status=1)).filter(bus_name=id).count()
#         count2 = License_Info.objects.filter(Q(status=2) & Q(pay_status=1)).filter(bus_name=id).count()

#         # Calculate the total count of items with status = 0, 1, and 2
#         total_count = count0 + count1 + count2

#         if total_count == 0:
#             return 0.0  # Avoid division by zero

#         # Calculate the percentage of items with status = 0 and 1
#         percentage = ((count0 + count1) / total_count) * 100

#         # Round to 1 decimal place
#         return round(percentage, 1)

#     except Exception as e:
#         print(f"Error: {e}")
#         return 0.0  # Return 0 or handle the error as needed

# @register.simple_tag
# def compliance_status(id):
#     _perc_overrall = calculate_percentage_bus(id)
#     _result = ''
#     if int(_perc_overrall) > 0.0:
#         _result = f'''<span class="badge bg-danger">Non-Compliant</span>'''
#     else:
#         _result = f'''<span class="badge bg-success">Compliant</span>'''
#     return _result

# @register.simple_tag
# def compliance_status_lg(id):
#     _perc_overrall = calculate_percentage_bus(id)
#     _result = ''
#     if int(_perc_overrall) > 0.0:
#         _result = f'''<span class="badge bg-danger badge-lg">Non-Compliant</span>'''
#     else:
#         _result = f'''<span class="badge bg-success badge-lg">Compliant</span>'''
#     return _result

# @register.simple_tag
# def compliance_percentage(id):
#     _perc_overrall = calculate_percentage_bus(id)
#     if _perc_overrall <= 0.0:
#         _x = 100 - ((_perc_overrall * 1.0) * 1.0)
#         _result = f'{_x}%'
#     else:
#         _x = 100 - ((_perc_overrall * 1.0) * 1.0)
#         _result = f'{_x}%'
#     return _result

# @register.simple_tag
# def current_year_revenue():
#     current_year = timezone.now().year
#     # if year == current_year:
#     revenue = DataPoint.objects.filter(year=current_year).aggregate(total_revenue=Sum('value'))['total_revenue']
#     return format(revenue, ",") if format(revenue, ",") else 0
#     # else:
#     #     return 0

# @register.simple_tag
# def previous_year_revenue():
#     current_year = timezone.now().year
#     previous_year = current_year - 1
#     # if year == current_year:
#     revenue = DataPoint.objects.filter(year=previous_year).aggregate(total_revenue=Sum('value'))['total_revenue']
#     return format(revenue, ",") if format(revenue, ",") else 0
#     # else:
#     #     return 0
    
# @register.simple_tag
# def year_revenue(year):
#     current_year = timezone.now().year
#     previous_year = current_year - 1
#     print(year)
#     # if year == current_year:
#     revenue = DataPoint.objects.filter(year=year).aggregate(total_revenue=Sum('value'))['total_revenue']
#     # return format(revenue, ",") if format(revenue, ",") else 0
#     return revenue
#     # else:
#     #     return 0
    
# @register.simple_tag
# def current_year_revenue_department(id):
#     current_year = timezone.now().year
#     # if year == current_year:
#     revenue = DataPoint.objects.filter(Q(year=current_year) & Q(licId=id)).aggregate(total_revenue=Sum('value'))['total_revenue']
#     return format(revenue, ",") if format(revenue, ",") else 0
#     # else:
#     #     return 0

# @register.simple_tag
# def previous_year_revenue_department(id):
#     current_year = timezone.now().year
#     previous_year = current_year - 1
#     # if year == current_year:
#     revenue = DataPoint.objects.filter(Q(year=previous_year) & Q(licId=id)).aggregate(total_revenue=Sum('value'))['total_revenue']
#     return format(revenue, ",") if format(revenue, ",") else 0
#     # else:
#     #     return 0

# #///////////////////////////////////////////////////////////////
# #///////////////////////////////////////////////////////////////

# @register.simple_tag
# def get_org_name(owner):
#     usr = Organizations.objects.get(orgId=owner)
#     # sr_ = ""
#     if usr is None:
#         sr_ = "Unknown Organization"
#     else:
#         sr_ = usr.orgName
#     return str(sr_)

# @register.simple_tag
# def get_org_logo(owner):
#     usr = Organizations.objects.get(orgId=owner)
#     logoFile_ = usr.orgLogo
#     fileDir_ = usr.orgId
#     sr_=logoFile_
#     return str(sr_)

# @register.simple_tag
# def get_depart_list(owner):
#     orgId = Organizations.objects.get(orgId=owner)
#     dpInstance = DepartClass.objects.filter(orgId=orgId)
#     return dpInstance.values_list('departName')

# @register.simple_tag
# def get_depart_name(depart):
#     # orgId = Organizations.objects.get(orgId=owner)
#     dpInstance = DepartClass.objects.get(departId=depart)
#     if dpInstance is None:
#         sr_ = "Unknown Department"
#     else:
#         sr_ = dpInstance.departName
#     return str(sr_)

# @register.simple_tag
# def get_depart_name(owner):
#     departId = DepartClass.objects.get(departId=owner)
#     departName = departId.departName
#     return str(departName)

# @register.simple_tag
# def get_user_part(owner):
#     own = ast.literal_eval(owner)
#     list_names = []
#     for i in own:
#         names_ = CustomUser.objects.get(uid=i)
#         dices = names_.fname+" "+names_.sname
#         list_names.append(dices)
#     dr_ = str(list_names)
#     dr_1 = dr_.replace("'", '')
#     dr_2 = dr_1.replace("[", '')
#     dr_3 = dr_2.replace("]", '')
#     return str(dr_3)

@register.simple_tag
def get_user_name_via_uid(owner):
    usr = CustomUser.objects.filter(uid=owner).first()
    if usr is None:
        sr = "Unknown User"
    else:
        sr = f'{usr.fname} {usr.sname}'
    return sr

# @register.simple_tag
# def get_depart_list(owner):
#     orgId = Organizations.objects.get(orgId=owner)
#     dpInstance = DepartClass.objects.filter(orgId=orgId)
#     return dpInstance.values_list('departName')

# @register.simple_tag
# def get_depart_name(depart):
#     # orgId = Organizations.objects.get(orgId=owner)
#     dpInstance = DepartClass.objects.get(departId=depart)
#     if dpInstance is None:
#         sr_ = "Unknown Department"
#     else:
#         sr_ = dpInstance.departName
#     return str(sr_)

# @register.simple_tag
# def get_departs_name(owner):
#     departId = DepartClass.objects.get(departId=owner)
#     departName = departId.departName
#     return str(departName)

# @register.simple_tag
# def depart_user_count(id):
#     activecount = DepartUsers.objects.filter(departId=id).count()
#     return format(activecount, ",")

# @register.simple_tag
# def sub_depart_count(id):
#     activecount = DepartSubClass.objects.filter(departSubId=id).count()
#     return format(activecount, ",")

#///////////////////////////////////////////////////////////////
#/////////////////////// UAC HEADER ////////////////////////////
# from django.http import HttpResponse
# from django.utils.html import escape
# @register.simple_tag
# def uac_perm_analytics(owner):
#     _type = Access_Rights.objects.get(field_name='analytics_field')
#     usr = User_Access_Rights.objects.get(Q(uac_owner=owner) & Q(uac=_type.id))
#     if usr.status == '1':
#         response = f"<li class='side-nav-item'><a href='/analytics' class='side-nav-link'><i class='uil-chart-pie-alt'></i><span> Analytics </span></a></li>"
#         return response
#     else:
#         return ''

# @register.simple_tag
# def uac_perm_node(owner):
#     _type = Access_Rights.objects.get(field_name='node_field')
#     usr = User_Access_Rights.objects.get(Q(uac_owner=owner) & Q(uac=_type.id))
#     if usr.status == '1':
#         response = f'''
#         <li class="side-nav-item">
#         <a href="/nodes" class="side-nav-link">
#           <i class="uil-location-point"></i>
#           <span> Stations </span>
#         </a>
#       </li>
#         '''
#         return response
#     else:
#         return ''

# @register.simple_tag
# def uac_perm_regis(owner):
#     _type = Access_Rights.objects.get(field_name='regis_field')
#     usr = User_Access_Rights.objects.get(Q(uac_owner=owner) & Q(uac=_type.id))
#     if usr.status == '1':
#         response = f'''
#         <li class="side-nav-item">
#         <a href="/registration" class="side-nav-link">
#           <i class="uil-store"></i>
#           <span> Registration </span>
#         </a>
#       </li>
#         '''
#         return response
#     else:
#         return ''

# @register.simple_tag
# def uac_perm_depart(owner):
#     _type = Access_Rights.objects.get(field_name='depart_field')
#     usr = User_Access_Rights.objects.get(Q(uac_owner=owner) & Q(uac=_type.id))
#     if usr.status == '1':
#         response = f'''
#         <li class="side-nav-item">
#         <a href="/nodes/departments" class="side-nav-link">
#           <i class="uil-briefcase"></i>
#           <span> Departments </span>
#         </a>
#       </li>
#         '''
#         return response
#     else:
#         return ''

# @register.simple_tag
# def uac_perm_approval(owner):
#     _type = Access_Rights.objects.get(field_name='approval_field')
#     usr = User_Access_Rights.objects.get(Q(uac_owner=owner) & Q(uac=_type.id))
#     if usr.status == '1':
#         response = f'''
#         <li class="side-nav-item">
#         <a href="/approvals" class="side-nav-link">
#           <i class="uil-document-layout-center"></i>
#           <span> Approvals </span>
#         </a>
#       </li>
#         '''
#         return response
#     else:
#         return ''

# @register.simple_tag
# def uac_perm_license(owner):
#     _type = Access_Rights.objects.get(field_name='license_field')
#     usr = User_Access_Rights.objects.get(Q(uac_owner=owner) & Q(uac=_type.id))
#     if usr.status == '1':
#         response = f'''
#         <li class="side-nav-item">
#         <a href="/licenses" class="side-nav-link">
#           <i class="uil-layer-group"></i>
#           <span> Licenses </span>
#         </a>
#       </li>
#         '''
#         return response
#     else:
#         return ''
    
# @register.simple_tag
# def uac_perm_security(owner):
#     _type = Access_Rights.objects.get(field_name='security_field')
#     usr = User_Access_Rights.objects.get(Q(uac_owner=owner) & Q(uac=_type.id))
#     if usr.status == '1':
#         response = f'''
#         <li class="side-nav-item">
#         <a href="/security" class="side-nav-link">
#           <i class="uil-shield-check"></i>
#           <span> Security </span>
#         </a>
#       </li>
#         '''
#         return response
#     else:
#         return ''
    
#///////////////////////////////////////////////////////////////


#/////////////////// PERMISSIONS SECTION ///////////////////////
# @register.simple_tag
# def get_uac_permisions(id, userkey):
#     permits = User_Access_Rights.objects.filter(Q(uac=id) & Q(uac_owner=userkey))
#     resp = ''
#     for perm in permits:
#         if perm.status == '0':
#             resp = f'unchecked'
#         elif perm.status == '1':
#             resp = f'checked'
#         return resp

#///////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////


import qrcode

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f'static/qr_store/{filename}')
    return 1

@register.simple_tag
def get_qr_code(id):
    vr_ = f'static/qr_store/{id}.png'
    vr_ = f'<img src="{vr_}" style="height: 120px; width: 120px;" title="QR_CODE"/>'
    return vr_

@register.simple_tag
def format_currency(figure):
    _str = int(figure)
    _conv = format(_str, ",")
    return _conv

@register.simple_tag
def generate_unique_sku():
    prefix = "VPID"
    unique_id = f"{prefix}-{str(uuid4())[:8].upper()}"
    return unique_id