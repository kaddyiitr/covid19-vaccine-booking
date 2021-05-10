# Script for Vaccination Slot Booking

A python script that allows you to create end-to-end booking of vaccination slot

## Installation

User **Python 3.6+** and install all the dependencies with the following command. Its best to do so in a virtual environment.

```
pip3 install -r requirements.txt
```


## Usage

To know about all the command line parameters supported by the script, use the following command

```
python covid-appointments.py -h
```

Apart from these inputs, ther script requires two more inputs. The Authentication token and the comma separated list of beneficiaries.

#### How to get the Authentication Token

To get the authentication token, follow these steps

- Open https://selfregistration.cowin.gov.in/ in chrome 
- Right Click on the page and click Inspect to open the Chrome DevTools. 
- Go to the Network tab and within that, open the XHR tab
- After successful OTP authentication, look for the beneficiaries API call
- From the Request Headers copy the authorisation header without Bearer. It starts with **ey**
- Refer to this link if you are still confused

#### How to get Beneficiaries

After successful login into the covid portal, you shall see the list of all the added members. Copy the REF ID (a 13 digit id displayed right next to the name) into a comma selarated list (without any spaces) and press enter.


## Limitations

- This script is tested only on a mac, might require minor tweaks to make it run on windows.
- The token expires every 15 minutes; you will have to generate a new token after each expiry
- All Beneficiaries need to be in the same age category. You cannot book 1 beneficiary in 18-44 category and another in 45+ category in one go. You will have to run the script separately for each one. 


