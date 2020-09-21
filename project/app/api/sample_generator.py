import numpy as np

from faker import Faker

from datetime import datetime
from datetime import timedelta
import math
import string
import random
import uuid
import secrets
import csv
from random import random, randrange, randint
import itertools

fake = Faker()


class sampleGenerator():
    """Construct a new user sample."""
    def __init__(self):
        self._ID_profiles = {}
        self._TXN_profiles = []

        self.configure_ID_profiles()
        self.configure_TXN_profiles()


    def configure_ID_profiles(self, k=1):
        self.handle_user_id(k=k)
        self.handle_account_subtype(k=k)
        self.handle_start_time(k=k)

        self._ID_profiles["user_id"] = self._user_id
        self._ID_profiles["user_location"] = self.handle_user_location(k=k)
        # # self._ID_profiles["current_balance"] = ""
        self._ID_profiles["plaid_account_id"] = self.handle_user_plaid_id(k=k)
        self._ID_profiles["plaid_financial_authentication_id"] = self.handle_user_plaid_authentication_id(k=k)
        self._ID_profiles["start_time"] = self._start_time
        self._ID_profiles["type"] = self.handle_constant("PlaidBankAccount", k=k)
        self._ID_profiles["account_subtype"] = self._account_subtype
        self._ID_profiles["main_saving"] = self.handle_constant("True", k=k)
        self._ID_profiles["plaid_state"] = self.handle_constant("Connected", k=k)

        return self._ID_profiles


    def configure_TXN_profiles(self, k=1):
        self._TXN_profiles = self.handle_account_transactions(k=k)

        return self._TXN_profiles


    """<------------------------------------->
       <----- handle user ID generation ----->
       <------------------------------------->"""
    def handle_constant(self, string="", k=1):
        """ handles placeholder information. """
        cache = [string] * k
        
        return cache
        
        
    def handle_user_id(self, k=1):
        """ returns a user identification number. """
        cache = {}
        
        while len(cache) < k:
            user_id = "1" + str(f'{randrange(1, 10**9):09}')
            if user_id not in cache:
                cache[user_id] = 1
            else:
                pass
    
        self._user_id = [x for x in cache]

        return self._user_id


    def handle_user_plaid_id(self, k=1):
        """ returns a user plaid hash-type identification. """
        cache = {}
        
        while len(cache) < k:
            user_plaid_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(37))
            if user_plaid_id not in cache:
                cache[user_plaid_id] = 1
            else:
                pass

        result = [x for x in cache]

        return result


    def handle_user_plaid_authentication_id(self, k=1):
        """ return a user plaid identification number. """
        cache = {}
        
        while len(cache) < k:
            user_plaid_authentication_id = "5" + str(f'{randrange(1, 10**9):09}')
            if user_plaid_authentication_id not in cache:
                cache[user_plaid_authentication_id] = 1
            else:
                pass
            
        result = [x for x in cache]

        return result


    def handle_start_time(self, k=1):
        """ returns a random account start datetime. """
        self._start_time = []

        for i in range(k):
            self._start_time.append(self.random_datetime())

        return self._start_time


    # def handle_goal_start_date(self):
    #     """ returns a random user goal start datetime. """
    #     start_time = self._user_start_time
    #     end_time = self._user_start_time + timedelta(months=rndint(1, 3))
    #     self._user_goal_start_time = random_datetime(self, start_time=start_time, end_time=end_time)
        
    #     return self._user_goal_start_time


    def handle_account_subtype(self, k=1):
        """ returns a starting account subtype based on observe distribution from
            client database. """
        self._account_subtype = []
    
        account_type_distribution = [10, 5, 7]
        account_type = ["checking", "saving", "paypal"]
        
        for i in range(k):
            self._account_subtype.append(self.weighted_choice(account_type, account_type_distribution))

        return self._account_subtype    


    def handle_user_location(self, k=1):
        """ returns a random user location based on historical population data of the U.S.A. """
        cache = []
        
        states = ["California", "Texas", "Florida", "New York", "Pennsylvania", "Illinois", "Ohio", "Georgia", "North Carolina", 
            "Michigan", "New Jersey", "Virginia", "Washington", "Arizona", "Massachusetts", "Tennessee", "Indiana", "Missouri",
            "Maryland", "Wisconsin", "Colorado", "Minnesota", "South Carolina", "Alabama", "Louisiana", "Kentucky", "Oregon", 
            "Oklahoma", "Connecticut", "Utah", "Puerto Rico", "Iowa", "Nevada", "Arkansas", "Mississippi", "Kansas", "New Mexico", 
            "Nebraska", "West Virginia", "Idaho", "Hawaii", "New Hampshire", "Maine", "Montana", "Rhode Island", "Delaware", 
            "South Dakota", "North Dakota", "Alaska", "District of Columbia", "Vermont", "Wyoming", "Guam", "U.S. Virgin Islands", 
            "Northern Mariana Islands", "American Samoa"]

        states_population = [39512223, 28995881, 21477737, 19453561, 12801989, 12671821, 11689100, 10617423, 10488084, 9986857, 
                            8882190, 8535519, 7614893, 7278717, 6892503, 6829174, 6732219, 6137428, 6045680, 5822434, 5758736, 
                            5639632, 5148714, 4903185, 4648794, 4467673, 4217737, 3956971, 3565287, 3205958, 3193694, 3155070, 
                            3080156, 3017804, 2976149, 2913314, 2096829, 1934408, 1792147, 1787065, 1415872, 1359711, 1344212, 
                            1068778, 1059361, 973764, 884659, 762062, 731545, 705749, 623989, 578759, 168485, 106235, 51433, 49437]

        total = sum(states_population)
        weights = [(pop / total) for pop in states_population]
        for i in range(k):
            cache.append(self.weighted_choice(states, states_population))

        return cache


    """<-------------------------------------->
       <----- handle user TXN generation ----->
       <-------------------------------------->"""

    def handle_account_transactions(self, k=1):
        """ returns a starting transaction profile used to create a transaction 
            history based on available data distribution. """
        cache = {}
        
        saving_distribution = [0, 0, 0, 0, 12, 0, 0, 27, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 27, 0, 0, 0, 
                               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 2, 0, 247, 0, 0]
        saving_distribution_normal = self.normalize_array(saving_distribution, tmax=100)
        
        paypal_distribution = [0, 0, 7, 2, 0, 134, 11, 7, 0, 53, 0, 1, 2, 0, 1, 1, 18, 0, 0, 5, 129, 0, 12, 0, 0, 0, 18, 
                               0, 0, 0, 0, 0, 0, 0, 44, 0, 1, 0, 2, 1, 0, 175, 169, 544, 0, 0, 113, 21, 681, 5, 1]
        paypal_distribution_normal = self.normalize_array(paypal_distribution, tmax=100)


        """ provide an initial transaction category 'weights' array based on 
        distribution observed from client database. """
        counter = 0
        for i in self._account_subtype:
            for m in self._user_id:
                if i is "checking":
                    cache[m] = self.handle_checking_transactions(index=counter)
                if i is "saving":
                    cache[m] = self.handle_checking_transactions(index=counter)
                    # cache[m] = self.handle_saving_transactions()
                if i is "paypal":
                    cache[m] = self.handle_checking_transactions(index=counter)
                    # cache[m] = self.handle_paypal_transactions()


        return cache
    
    def handle_checking_transactions(self, index, k=1):
        # available categories, index sensitive.
        parent_category_distribution = ['Advertising and Marketing', 'Agriculture and Forestry', 'Air Travel', 'Arts and Entertainment', 
                                'ATM', 'Auto Transportation', 'Automotive', 'Bank Fees', 'Business Services', 'Car Service', 
                                'Check', 'Clothing and Accessories', 'Community Services', 'Computers', 'Credit Card', 'Education', 
                                'Electronics', 'Entertainment', 'Financial', 'Food Delivery Services', 'Food and Beverage Store', 
                                'Government Departments and Agencies', 'Government Support', 'Healthcare', 'Home Improvement', 
                                'Interest', 'Loans and Mortgages', 'Lodging', 'Manufacturing', 'Mining', 'Nightlife', 'Other Travel', 
                                'Outlet', 'Parks', 'Payroll', 'Personal Care', 'Public Transit', 'Real Estate', 'Recreation', 
                                'Religious', 'Rent', 'Restaurants', 'Service', 'Shops', 'Student Aid and Grants', 'Taxes', 
                                'Third Party', 'Savings Apps', 'Transfer', 'Utilities', 'Payment']
    
        # initial set of 'weights' used for transaction distribution.
        checking_distribution = [0, 0, 1, 8, 77, 162, 38, 8, 0, 11, 2, 4, 0, 0, 0, 0, 3, 0, 1, 2, 149, 0, 30, 4, 0, 2, 15, 
                                 2, 0, 0, 0, 8, 0, 0, 64, 1, 0, 0, 0, 0, 0, 149, 326, 478, 0, 1, 204, 0, 977, 2, 0]
        checking_distribution_normal = self.normalize_array(checking_distribution, tmax=100)
        
        cache = {"plaid_transaction_id": [],
                 "date": [],
                 "amount_cents": [],
                 "category_id": [],
                 "category_name": [],
                 "parent_name": [],
                 "iso_currency_code": []
                 }

        k = randint(1 , 100)
        for i in range(k):
            cache["plaid_transaction_id"].append("plaid_transaction_id")
            # cache["category_id"] = self.handle_category_identify()

            start_time = self._start_time[index]                                                                        #>>> TODO
            cache["date"].append(self.random_datetime())
            # cache["date"] = self._start_time[index]

            cache["amount_cents"].append(randint(-100000, 100000))
            
            cache["category_id"].append("21002002")

            cache["category_name"].append(self.weighted_choice(parent_category_distribution, checking_distribution_normal))

            cache["parent_name"].append("parent_name")
            
            cache["iso_currency_code"].append("USD")
        
        return cache
    
    
    def handle_category_identify(self):
        pass


    """<------------------------------------->
       <----- utility/support functions ----->
       <------------------------------------->"""
    def weighted_choice(self, objects, weights):
        """ returns randomly an element from the sequence of 'objects',
            the likelyhood of the objects is weighted according to the
            sequence of 'weights', i.e. percentages."""
        weights = np.array(weights, dtype=np.float64)
        sum_of_weights = weights.sum()
        np.multiply(weights, 1 / sum_of_weights, weights)
        weights = weights.cumsum()
        x = random()
        for i in range(len(weights)):
            if x < weights[i]:
                return objects[i]
            
            
    def normalize_array(self, array, tmin=0, tmax=10):
        tmin, tmax = tmin, tmax
        amin, amax = min(array), max(array)
        for i, val in enumerate(array):
            array[i] = round(((val - amin)/(amax - amin)) * (tmax - tmin) + tmin, 3)

        return array        


    def random_datetime(self, start_time='2018-01-01 00:00:00', end_time='2020-01-01 00:00:00'):
        """ returns randomly a datetime between 'start', and 'end'."""
        date_obj_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        date_obj_end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        random_date_obj = fake.date_time_between(start_date=date_obj_start, end_date=date_obj_end)

        return random_date_obj.strftime("%Y-%m-%d %H:%M:%S")

    
    def wave_constructor(self, wave=None, amplitude=1, frequency=0.05, offset=0, bias=[], update=False):
        """ returns an array of 'weights' based on random mathematical equations. """
        array = [0] * 50

        if wave is "sin":
            for i in range(50):
                array[i] = (amplitude * math.sin(i * frequency)) + offset
        if wave is "tan":
            for i in range(50):
                array[i] = (amplitude * math.tan(i * frequency)) + offset
        if wave is "tanh":
            for i in range(50):
                array[i] = (amplitude * math.tanh(i * frequency)) + offset
        if wave is "exp":
            for i in range(50):
                array[i] = (amplitude * math.exp(i * frequency)) + offset
        if wave is "inv_exp":
            for i in range(50):
                array[i] = (amplitude * math.exp(-i * frequency)) + offset
        if wave is "outlier":
            for i in bias:
                array[i] =+ 5

        return array

                
    def ID_profile_csv(self,  function=True):
        fields = list(self._ID_profiles.keys())

        v = list(self._ID_profiles.values())
        rows = [list(i) for i in zip(*v)]


        filename = "data/user_id.csv"

        if function is True:
            print(f"{fields}\n{rows}")
        else:        

            # writing to csv file  
            with open(filename, 'w', newline='') as csvfile:  
                # creating a csv writer object  
                csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)  
                    
                # writing the fields  
                csvwriter.writerow(fields)  
                    
                # writing the data rows  
                csvwriter.writerows(rows)

  
    def TXN_profile_csv(self, function=True):
        for k, v in self._TXN_profiles.items():
            fields = list(v.keys())
            
        fields.insert(0, "user_id")

        cache = []
        for i in self._TXN_profiles:
            v = (self._TXN_profiles[i].values())
            rows = [list(i) for i in zip(*v)]
            for n in rows:
                n.insert(0, i)
            for k in rows:
                cache.append(k)

        filename = "data/user_transaction.csv"
        
        if function is True:
            print(f"{fields}\n{cache}")
        else:

            # writing to csv file  
            with open(filename, 'w', newline='') as csvfile:  
                # creating a csv writer object  
                csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)  
                    
                # writing the fields  
                csvwriter.writerow(fields)  
                    
                # writing the data rows  
                csvwriter.writerows(cache)



if __name__ == "__main__":
    """ testing sample generation. """
    sample_user = sampleGenerator()

    sample_user.configure_ID_profiles(k=10)
    sample_user.ID_profile_csv(function=False)
    sample_user.configure_TXN_profiles(k=10)
    sample_user.TXN_profile_csv(function=False)