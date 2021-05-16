# Script for Vaccination Slot Booking

A python script that allows you to create end-to-end booking of vaccination slot

## Installation

User **Python 3.6+** and install all the dependencies with the following command. Its best to do so in a virtual environment.

```
pip3 install -r requirements.txt
```


## Usage

**The first step before running this script is to add all the people you want to book appointments for, into one single account.** This way, you can book all of them in one single appointment itself.  

To know about all the command line parameters supported by the script, use the following command

```
python3 covid-appointments.py -h
```

Apart from the command line inputs provided to the script at the time of starting the script, two more inputs are required - **Authentication token** and **Beneficiaries**. The script will ask for these inputs after you run it and will not proceed further until you provide these inputs.

#### How to get the Authentication Token

To get the authentication token, follow these steps

- Open https://selfregistration.cowin.gov.in/ in Chrome Browser.
- Right Click on the page and click Inspect to open the Chrome DevTools. 
- Go to the Network tab and within that, open the XHR tab
- After successful OTP authentication, look for the beneficiaries API call
- From the Request Headers copy the authorisation header without Bearer. It starts with **ey**
- If you are still confused, refer to this [screenshot](https://raw.githubusercontent.com/kaddyiitr/covid19-vaccine-booking/master/help-screenshot.png) and pay attention to the parts circled in red color.


## Examples

1. For booking first Dose in 18-44 age category for 1 person (with REF ID 2371875657319) in Belagum for today
```
python3 covid-appointments.py --district 264 --beneficiaries 2371875657319
```

2. For booking first Dose in 45+ age category for two people in Bangalore on 17th May'21 preferring nearby hospitals first, say pincodes 560102 and 560034
```
python3 covid-appointments.py --age 45 --district 294 --beneficiaries 2371875657319,7265471323123 --pin 560102,560034
```

3. For booking second Dose of COVIDSHIELD in 45+ age category for Bangalore on 17th May'21 restricting bookings to hospitals in the pincodes 560102 and 560034. With this command, any hospital providing COVAXIN will be ignored.
```
python3 covid-appointments.py --dose 2 --age 45 --beneficiaries 2371875657319 --type COVIDSHIELD --district 294 --pin 560102,560034 --restrictpin yes
```

### How to get Beneficiaries

After successful login into the covid portal, you shall see the list of all the added members. Copy the REF ID (a 13 digit id displayed right next to the name) into a comma selarated list (without any spaces) and pass it in the --beneficiaries parameter

### How to get district Id

Please refer to the [districts.csv](https://github.com/kaddyiitr/covid19-vaccine-booking/blob/master/districts.csv) sheet. It contains the list of all district_ids in the country


## Limitations

- This script is tested only on a mac, might require minor tweaks to make it run on windows.
- The token expires every 15 minutes; you will have to generate a new token after each expiry
- All Beneficiaries need to be in the same age category. You cannot book 1 beneficiary in 18-44 category and another in 45+ category in one go. You will have to run the script separately for each one. 


