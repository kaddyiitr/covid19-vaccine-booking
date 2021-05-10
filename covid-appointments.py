import requests
import sys
import datetime
import pprint
import json
import hashlib
import os
import time
import traceback

from svglib.svglib import svg2rlg
import io
import uuid
import argparse


RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"
TOKEN_FILE = "token.txt"

SLEEP = 3
AGE = 18
DISTRICT = 294
DOSE = 1


def get_headers(token=None):
    headers = {'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.9',
        'authority': 'cdn-api.co-vin.in',
        'cache-control': 'no-cache',
        'origin': 'https://selfregistration.cowin.gov.in',
        'pragma': 'no-cache',
        'referer': 'https://selfregistration.cowin.gov.in/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
    if token:
        headers['Authorization'] = "Bearer "+token
    return headers

def cprint(string, color):
    sys.stdout.write(color)
    print(string)
    sys.stdout.write(RESET)

def get_token():
    token = None

    print("Enter token:")
    token = input()
    if token:
        return token

'''
    print("Mobile:")
    mobile=input()
    headers = get_headers()
    if mobile:
        print(mobile)
        r = requests.post("https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP", json= {"mobile": mobile},headers=headers)
        print(r.status_code)
        txnId = r.json()['txnId']
        print ("OTP:")
        otp=input()
        if otp:
            r = requests.post("https://cdn-api.co-vin.in/api/v2/auth/public/confirmOTP", json = {"otp": hashlib.sha256(otp.encode()).hexdigest(), "txnId": txnId},headers=headers)
            token = r.json()['token']
    print(token)
    return token
'''


def fetch_sessions_of_interest(token, min_age_limit=18, district_id=294,date=None, vaccine_type = None):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={district_id}&date={date}".format(date=date,district_id=district_id)
    headers = get_headers(token)
    r=requests.get(url,headers=headers)
    centers = r.json()['centers']
    useful_sessions = []
    for center in centers:
        row = {"center_id" : center['center_id'], 'pincode' : center['pincode'], 'name': center['name']}
        for session in center['sessions']:

            if vaccine_type and vaccine_type != session['vaccine']:
                continue

            if (session['available_capacity'] > 0 and session['min_age_limit'] == min_age_limit):
                myrow = row.copy()
                myrow.update(session)
                useful_sessions.append(myrow)
    return useful_sessions

def get_beneficiaries(token):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries"
    headers = get_headers(token)
    r=requests.get(url,headers=headers)
    if r.status_code != 200:
        cprint ("Get beneficiaries failed. Please login again", CYAN)
        exit(1)
        return default_beneficiaries
    return r.json()['beneficiaries']


def are_all_appointments_in_past(appointments):
    all_past_appointments = True
    pprint.pprint(appointments)
    for appointment in appointments:
        appointment_date_str = appointment['date'] + " 00:00:00"
        appointment_date = datetime.datetime.strptime(appointment_date_str,'%d-%m-%Y %H:%M:%S')
        today = datetime.date.today()
        if appointment_date.date() >= today:
            all_past_appointments = False
            break

    return all_past_appointments



def are_all_appointments_booked(beneficiaries,beneficiary_ids, dose):
    for beneficiary in beneficiaries:
        if beneficiary["beneficiary_reference_id"] in beneficiary_ids and (len(beneficiary['appointments']) == 0 or are_all_appointments_in_past(beneficiary['appointments'])):
            return False
    return True


#function not used
def get_unbooked_beneficiaries(beneficiaries,beneficiary_ids, dose):

    unbooked_beneficiaries = []

    for beneficiary in beneficiaries:
        if beneficiary["beneficiary_reference_id"] in beneficiary_ids and len(beneficiary['appointments']) == 0:
            unbooked_beneficiaries.append(beneficiary)
            continue

        #check an appointment is already booked, then check if the appointment is in future. If in future, return True
        future_appointments = False
        pprint.pprint(beneficiary)
        for appointment in beneficiary['appointments']:
            appointment_date_str = appointment['date'] + " 00:00:00"
            appointment_date = datetime.datetime.strptime(appointment_date_str,'%d-%m-%Y %H:%M:%S')
            today = datetime.date.today()
            if appointment_date.date() > today:
                future_appointments = True
                break

        if not future_appointments:
            unbooked_beneficiaries.append(beneficiary)


    return unbooked_beneficiaries


def saveAsPNG(captchaStr):
    svg_io = io.StringIO(captchaStr)
    drawing = svg2rlg(svg_io)
    png_str = drawing.asString("png")
    byte_io = io.BytesIO(png_str)

    filename = str(uuid.uuid4())
    filepath = '/tmp/' + filename + ".png"
    f = open(filepath, 'wb')
    f.write(byte_io.getvalue())
    f.close()
    return filepath

def readCaptcha(token):
    captchaStr = getCaptcha(token)
    filepath = saveAsPNG(captchaStr)
    os.system('open ' + filepath)
    print ("Please Enter the Captcha")
    captcha = input()
    print ("The captcha you entered: " + captcha)
    return captcha

def getCaptcha(token):
    data = {}
    url = "https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha"
    headers = get_headers(token)
    r=requests.post(url, json=data, headers=headers)
    success = (r.status_code == 200)
    if success:
        return r.json()['captcha']
    else:
        return False


def book_appointments_for_session(token, session, beneficiary_ids, dose):
    slots = session["slots"]
    slot = None
    if len(slots) == 0: return False
    if len(slots) >=2:
        slot = slots[0]
    else:
        slot = slots[0]

    #Call getCatcha 
    captchaResp = readCaptcha(token)

    if not captchaResp:
        cprint("Invalid Captcha Entered", RED)
        return False


    data = {"dose": dose, "session_id": session["session_id"], "slot":slot,"beneficiaries": beneficiary_ids, "captcha" : captchaResp , "center_id": session["center_id"]}
    pprint.pprint(data)
    url = "https://cdn-api.co-vin.in/api/v2/appointment/schedule"
    headers = get_headers(token)
    pprint.pprint(headers)
    r=requests.post(url, json=data, headers=headers)
    success = (r.status_code == 200)
    if success:
        print("appointment_confirmation_number: ",r.json())
    else:
        cprint("failed to book appointment at {0}. Error: {1}".format(session['name'],r.text),CYAN)
    return success

def attempt_appointments(token,useful_sessions,beneficiary_ids, dose):
    beneficiaries = get_beneficiaries(token)

    if are_all_appointments_booked(beneficiaries,beneficiary_ids, dose):
        cprint("APPOINTMENT ALREADY BOOKED!!", GREEN)
        return True

    for session in useful_sessions:
        ret = book_appointments_for_session(token, session, beneficiary_ids, dose)
        if ret == True:
            beneficiaries = get_beneficiaries(token)
            if are_all_appointments_booked(beneficiaries,beneficiary_ids, dose):
                cprint("SUCCESSFULLY BOOKED ALL APPOINTMENTS", GREEN)
                return True
    return False


def get_beneficary_ids():
    print("Enter Beneficiary ID:")
    t = input()
    t = t.split(",")
    t = [i.strip() for i in t]
    return t

def main():


    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", help = "Date for search DD-MM-YYYY format. Default value Today")
    parser.add_argument("-a", "--age", help = "Age for 18-45, pass 18; 45-60, pass 45. Default value 18")
    parser.add_argument("-b", "--dose", help = "For first dose, pass 1; for second dose pass 2. Default value 1")
    parser.add_argument("-t", "--type", help = "COVAXIN or COVIDSHIELD")
    parser.add_argument("-l", "--district", help = "district id. Default value 294, for Bangalore")


    # Read arguments from command line
    args = parser.parse_args()

    age = AGE 
    if args.age:
        age = int(args.age)

    district = DISTRICT
    if args.district:
        district = int(args.district)

    dose = DOSE
    if args.dose:
        dose = int(args.dose)

    today = datetime.datetime.now().strftime('%d-%m-%Y')
    date_str = today
    if args.date:
        date_str = args.date

    vaccine_type = None
    if args.type:
        if args.type.lower() == 'covaxin':
            vaccine_type = 'COVAXIN'
        else:
            vaccine_type = 'COVIDSHIELD'



    cprint("Searching Appointment for date " + date_str + " age " + str(age) + " dose " + str(dose) + " district " + str(district),CYAN)

    token = get_token()


    useful_sessions = fetch_sessions_of_interest(token, age, district, date_str, vaccine_type)
    pprint.pprint(useful_sessions)
    beneficiary_ids = get_beneficary_ids()
    i=0
    while True:
        i+=1
        try:
            useful_sessions = fetch_sessions_of_interest(token, age, district, date_str, vaccine_type)
        except:
            traceback.print_exc()
            continue

        if len(useful_sessions) > 0:

            success = attempt_appointments(token,useful_sessions, beneficiary_ids, dose)
            if success:
                beneficiaries = get_beneficiaries(token)
                pprint.pprint(beneficiaries)
                exit(0)
        else:
            if i%12 == 0:
                get_beneficiaries(token)
            print("[%s] No Appointments, attempt %s " % (datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), str(i)), RED)
        time.sleep(SLEEP)

if __name__ == "__main__":
    main()
