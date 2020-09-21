from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
from pydantic import BaseModel, Field, validator
from fastapi.templating import Jinja2Templates
from typing import Optional
import json
import random

import sys
import traceback

from sktime.forecasting.model_selection import temporal_train_test_split
from sktime.performance_metrics.forecasting import smape_loss
from sktime.utils.plotting.forecasting import plot_ys
from sktime.forecasting.naive import NaiveForecaster
from sktime.forecasting.compose import ReducedRegressionForecaster
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor

import plotly.graph_objects as go

from dotenv import load_dotenv
from os.path import join, dirname
import os

from app.api.basemodels import User, GraphRequest


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


router = APIRouter()
templates = Jinja2Templates(directory="./app/static/dist")


class SaverlifeUtility(object):
    """General utility class to handle database cursor objects and other miscellaneous functions."""
    def __init__(self):
        self._cursor = self._handle_cursor()


    def _handle_connection(self):
        """Connect to a database."""
        return psycopg2.connect(
           host=os.getenv('POSTGRES_ADDRESS_EXTERNAL'),
           dbname=os.getenv('POSTGRES_DBNAME_EXTERNAL'),
           user=os.getenv('POSTGRES_USER_EXTERNAL'), 
           password=os.getenv('POSTGRES_PASSWORD_EXTERNAL'), 
           port=os.getenv('POSTGRES_PORT_EXTERNAL') 
        )

    def _handle_cursor(self):
        """Create a cursor to perform database operations."""
        conn = self._handle_connection()

        cur = conn.cursor()

        return conn, cur
    
    def handle_query(self, query: str, fetchone: bool = False):
        """Handle simple query operations."""
        try:
            conn, cur = self._handle_cursor()
            cur.execute(query)
        except BaseException:
            traceback.print_exc()
        finally:
            if cur:
                if fetchone is True:
                    try:
                        result = cur.fetchone()
                    except ProgrammingError:
                        result = None
                else:
                    result = cur.fetchall()
                cur.close()
                conn.close()
        return result

    def _generate_dataframe(self, table: str, bank_account_id: str = None, sample_size: int = 1):
        """Support utility function to handle database manipulation and other miscellaneous functions."""
        df = None

        if table is 'transactions':
            df = self._configure_transactions_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        if table is 'accounts':
            df = self._configure_accounts_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        if table is 'requests':
            df = self._configure_requests_dataframe()
        
        return df

    def _configure_transactions_dataframe(self, bank_account_id: str, sample_size: int = 1):
        df = self._fetch_transactions_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        
        df = self._wrangle_transactions(df)

        return df
    
    def _configure_accounts_dataframe(self, bank_account_id: str, sample_size: int = 1):
        df = self._fetch_accounts_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        
        df = self._wrangle_accounts(df)

        return df
    
    def _configure_requests_dataframe(self):
        df = self._fetch_requests_dataframe()
        
        df = self._wrangle_requests(df)

        return df
    
    def _handle_category_features(self, debug: bool = False):
        """Parse user category features from lists to a nested list for dataframe.
        
        Args:
            debug (bool): debug mode. Prints the result if TRUE else returns the result.
        Returns:
            list: nested list of features.
            
                [
                    [category_id], [category_name], [parent_category_name], [grandparent_category_name]
                ]
        """
        category_id = [
            '18001001', '18001002', '18001003', '18001004', '18001005', '18001006', '18001007', '18001008', '18001009', '18001010', '18073001', '18073002', '18073003', '18073004', '22001000', '22002000', '17001001', '17001002', '17001003', '17001004', '17001005', '17001006', '17001007', '17001008', '17001009', '17001010', '17001011', '17001012', '17001013', '17001014', '17001015', '17001016', '17001017', '17001018', '17001019', '17001000', '18020013', '21012002', '21007001', '21007002', '10002000', '22013000', '22017000', '22009000', '18006001', '18006002', '18006003', '18006004', '18006005', '18006006', '18006007', '18006008', '18006009', '19005001', '19005002', '19005003', '19005004', '19005005', '19005006', '19005007', '18006000', '10001000', '10003000', '10004000', '10005000', '10007000', '10008000', '10009000', '18008001', '22006001', '22006000', '22011000', '22016000', '21012001', '19012001', '19012002', '19012003', '19012004', '19012005', '19012006', '19012007', '19012008', '12002001', '12002002', '12001000', '12002000', '12003000', '12005000', '12006000', '12007000', '12015000', '12018000', '12019000', '12015001', '12015002', '12015003', '12019001', '18012001', '18012002', '16001000', '12008000', '12008001', '12008002', '12008003', '12008004', '12008005', '12008006', '12008007', '12008008', '12008009', '12008010', '12008011', '19013001', '19013002', '19013003', '18018001', '18020003', '18020005', '18020006', '18020007', '18020008', '18020009', '18020010', '18020011', '18020012', '18020014', '18021000', '18021001', '18021002', '19025000', '19025001', '19025002', '19025003', '19025004', '19047000', '12004000', '12010000', '12011000', '12012000', '12013000', '12014000', '12016000', '12017000', '12012001', '12012002', '12012003', '12009000', '21009001', '14001000', '14002000', '14001001', '14001002', '14001003', '14001004', '14001005', '14001006', '14001007', '14001008', '14001009', '14001010', '14001011', '14001012', '14001013', '14001014', '14001015', '14001016', '14001017', '14002001', '14002002', '14002003', '14002004', '14002005', '14002006', '14002007', '14002008', '14002009', '14002010', '14002011', '14002012', '14002013', '14002014', '14002015', '14002016', '14002017', '14002018', '14002019', '14002020', '18013001', '18013002', '18013003', '18013004', '18013005', '18013006', '18013007', '18013008', '18013009', '18013010', '18024001', '18024002', '18024003', '18024004', '18024005', '18024006', '18024007', '18024008', '18024009', '18024010', '18024011', '18024012', '18024013', '18024014', '18024015', '18024016', '18024017', '18024018', '18024019', '18024020', '18024021', '18024022', '18024023', '18024024', '18024025', '18024026', '18024027', '15001000', '15002000', '18020004', '16003000', '22012001', '22012002', '22012003', '22012004', '22012005', '22012006', '22012000', '18037001', '18037002', '18037003', '18037004', '18037005', '18037006', '18037007', '18037008', '18037009', '18037010', '18037011', '18037012', '18037013', '18037014', '18037015', '18037016', '18037017', '18037018', '18037019', '18037020', '18040001', '18040002', '18040003', '13001001', '13001002', '13001003', '13001000', '13002000', '13003000', '13004000', '13004001', '13004002', '13004003', '13004004', '13004005', '13004006', '22003000', '22004000', '22005000', '22007000', '22008000', '22010000', '22015000', '19040001', '19040002', '19040003', '19040004', '19040005', '19040006', '19040007', '19040008', '17023001', '17023002', '17023003', '17023004', '17025001', '17025002', '17025003', '17025004', '17025005', '17027001', '17027002', '17027003', '17027000', '21009000', '18045001', '18045002', '18045003', '18045004', '18045005', '18045006', '18045007', '18045008', '18045009', '18045010', '22014000', '22018000', '18050001', '18050002', '18050003', '18050004', '18050005', '18050006', '18050007', '18050008', '18050009', '18050010', '17002000', '17003000', '17004000', '17005000', '17006000', '17007000', '17008000', '17009000', '17010000', '17011000', '17012000', '17013000', '17014000', '17015000', '17016000', '17017000', '17018000', '17019000', '17020000', '17021000', '17022000', '17023000', '17024000', '17025000', '17026000', '17028000', '17029000', '17030000', '17031000', '17032000', '17033000', '17034000', '17035000', '17036000', '17037000', '17038000', '17039000', '17040000', '17041000', '17042000', '17043000', '17044000', '17045000', '17046000', '17047000', '17048000', '12018001', '12018002', '12018003', '12018004', '16002000', '13005000', '13005001', '13005002', '13005003', '13005004', '13005005', '13005006', '13005007', '13005008', '13005009', '13005010', '13005011', '13005012', '13005013', '13005014', '13005015', '13005016', '13005017', '13005018', '13005019', '13005020', '13005021', '13005022', '13005023', '13005024', '13005025', '13005026', '13005027', '13005028', '13005029', '13005030', '13005031', '13005032', '13005033', '13005034', '13005035', '13005036', '13005037', '13005038', '13005039', '13005040', '13005041', '13005042', '13005043', '13005044', '13005045', '13005046', '13005047', '13005048', '13005049', '13005050', '13005051', '13005052', '13005053', '13005054', '13005055', '13005056', '13005057', '13005058', '13005059', '18001000', '18003000', '18004000', '18005000', '18007000', '18008000', '18009000', '18010000', '18011000', '18012000', '18013000', '18014000', '18015000', '18016000', '18017000', '18018000', '18019000', '18020000', '18022000', '18023000', '18024000', '18025000', '18026000', '18027000', '18028000', '18029000', '18030000', '18031000', '18032000', '18033000', '18034000', '18035000', '18036000', '18037000', '18038000', '18039000', '18040000', '18041000', '18042000', '18043000', '18044000', '18045000', '18046000', '18047000', '18048000', '18049000', '18050000', '18051000', '18052000', '18053000', '18054000', '18055000', '18056000', '18057000', '18058000', '18059000', '18060000', '18061000', '18062000', '18063000', '18064000', '18065000', '18066000', '18067000', '18068000', '18069000', '18070000', '18071000', '18072000', '18073000', '18074000', '19001000', '19002000', '19003000', '19004000', '19005000', '19006000', '19007000', '19008000', '19009000', '19010000', '19011000', '19012000', '19013000', '19014000', '19015000', '19016000', '19017000', '19018000', '19019000', '19020000', '19021000', '19022000', '19023000', '19024000', '19026000', '19027000', '19028000', '19029000', '19030000', '19031000', '19032000', '19033000', '19034000', '19035000', '19036000', '19037000', '19038000', '19039000', '19040000', '19041000', '19042000', '19043000', '19044000', '19045000', '19046000', '19048000', '19049000', '19050000', '19051000', '19052000', '19053000', '19054000', '18020002', '18020001', '20001000', '20002000', '10006000', '21010001', '21010002', '21010003', '21010004', '21010005', '21010006', '21010007', '21010008', '21010009', '21010010', '21010011', '21001000', '21002000', '21003000', '21004000', '21005000', '21006000', '21007000', '21008000', '21010000', '21011000', '21012000', '21013000', '18068001', '18068002', '18068003', '18068004', '18068005'
            ]
        
        category_name = [
            'Writing, Copywriting and Technical Writing', 'Search Engine Marketing and Optimization', 'Public Relations', 'Promotional Items', 'Print, TV, Radio and Outdoor Advertising', 'Online Advertising', 'Market Research and Consulting', 'Direct Mail and Email Marketing Services', 'Creative Services', 'Advertising Agencies and Media Buyers', 'Crop Production', 'Forestry', 'Livestock and Animals', 'Services', 'Airlines and Aviation Services', 'Airports', 'Theatrical Productions', 'Symphony and Opera', 'Sports Venues', 'Social Clubs', 'Psychics and Astrologers', 'Party Centers', 'Music and Show Venues', 'Museums', 'Movie Theatres', 'Fairgrounds and Rodeos', 'Entertainment', 'Dance Halls and Saloons', 'Circuses and Carnivals', 'Casinos and Gaming', 'Bowling', 'Billiards and Pool', 'Art Dealers and Galleries', 'Arcades and Amusement Parks', 'Aquarium', 'Arts and Entertainment', 'ATMs', 'ATM', 'Check', 'ATM', 'ATM', 'Parking', 'Tolls and Fees', 'Gas Stations', 'Towing', 'Motorcycle, Moped and Scooter Repair', 'Maintenance and Repair', 'Car Wash and Detail', 'Car Appraisers', 'Auto Transmission', 'Auto Tires', 'Auto Smog Check', 'Auto Oil and Lube', 'Used Car Dealers', 'Salvage Yards', 'RVs and Motor Homes', 'Motorcycles, Mopeds and Scooters', 'Classic and Antique Car', 'Car Parts and Accessories', 'Car Dealers and Leasing', 'Automotive', 'Overdraft', 'Late Payment', 'Fraud Dispute', 'Foreign Transaction', 'Insufficient Funds', 'Cash Advance', 'Excess Activity', 'Printing and Publishing', 'Ride Share', 'Car Service', 'Limos and Chauffeurs', 'Taxi', 'Check', "Women's Store", 'Swimwear', 'Shoe Store', "Men's Store", 'Lingerie Store', "Kids' Store", 'Boutique', 'Accessories Store', 'Facilities and Nursing Homes', 'Caretakers', 'Animal Shelter', 'Assisted Living Services', 'Cemetery', 'Day Care and Preschools', 'Disabled Persons Services', 'Drug and Alcohol Services', 'Organizations and Associations', 'Religious', 'Senior Citizen Services', 'Youth Organizations', 'Environmental', 'Charities and Non-Profits', 'Retirement', 'Maintenance and Repair', 'Software Development', 'Credit Card', 'Education', 'Vocational Schools', 'Tutoring and Educational Services', 'Primary and Secondary Schools', 'Fraternities and Sororities', 'Driving Schools', 'Dance Schools', 'Culinary Lessons and Schools', 'Computer Training', 'Colleges and Universities', 'Art School', 'Adult Education', 'Video Games', 'Mobile Phones', 'Cameras', 'Media', 'Stock Brokers', 'Holding and Investment Offices', 'Fund Raising', 'Financial Planning and Investments', 'Credit Reporting', 'Collections', 'Check Cashing', 'Business Brokers and Franchises', 'Banking and Finance', 'Accounting and Bookkeeping', 'Food and Beverage', 'Distribution', 'Catering', 'Food and Beverage Store', 'Specialty', 'Health Food', 'Farmers Markets', 'Beer, Wine and Spirits', 'Supermarkets and Groceries', 'Courts', 'Government Lobbyists', 'Housing Assistance and Shelters', 'Law Enforcement', 'Libraries', 'Military', 'Post Offices', 'Public and Social Services', 'Police Stations', 'Fire Stations', 'Correctional Institutions', 'Government Departments and Agencies', 'Benefits', 'Healthcare Services', 'Physicians', 'Psychologists', 'Pregnancy and Sexual Health', 'Podiatrists', 'Physical Therapy', 'Optometrists', 'Nutritionists', 'Nurses', 'Mental Health', 'Medical Supplies and Labs', 'Hospitals, Clinics and Medical Centers', 'Emergency Services', 'Dentists', 'Counseling and Therapy', 'Chiropractors', 'Blood Banks and Centers', 'Alternative Medicine', 'Acupuncture', 'Urologists', 'Respiratory', 'Radiologists', 'Psychiatrists', 'Plastic Surgeons', 'Pediatricians', 'Pathologists', 'Orthopedic Surgeons', 'Ophthalmologists', 'Oncologists', 'Obstetricians and Gynecologists', 'Neurologists', 'Internal Medicine', 'General Surgery', 'Gastroenterologists', 'Family Medicine', 'Ear, Nose and Throat', 'Dermatologists', 'Cardiologists', 'Anesthesiologists', 'Specialty', 'Roofers', 'Painting', 'Masonry', 'Infrastructure', 'Heating, Ventilating and Air Conditioning', 'Electricians', 'Contractors', 'Carpet and Flooring', 'Carpenters', 'Upholstery', 'Tree Service', 'Swimming Pool Maintenance and Services', 'Storage', 'Roofers', 'Pools and Spas', 'Plumbing', 'Pest Control', 'Painting', 'Movers', 'Mobile Homes', 'Lighting Fixtures', 'Landscaping and Gardeners', 'Kitchens', 'Interior Design', 'Housewares', 'Home Inspection Services', 'Home Appliances', 'Heating, Ventilation and Air Conditioning', 'Hardware and Services', 'Fences, Fireplaces and Garage Doors', 'Electricians', 'Doors and Windows', 'Contractors', 'Carpet and Flooring', 'Carpenters', 'Architects', 'Interest Earned', 'Interest Charged', 'Loans and Mortgages', 'Loan', 'Resorts', 'Lodges and Vacation Rentals', 'Hotels and Motels', 'Hostels', 'Cottages and Cabins', 'Bed and Breakfasts', 'Lodging', 'Apparel and Fabric Products', 'Chemicals and Gasses', 'Computers and Office Machines', 'Electrical Equipment and Components', 'Food and Beverage', 'Furniture and Fixtures', 'Glass Products', 'Industrial Machinery and Equipment', 'Leather Goods', 'Metal Products', 'Nonmetallic Mineral Products', 'Paper Products', 'Petroleum', 'Plastic Products', 'Rubber Products', 'Service Instruments', 'Textiles', 'Tobacco', 'Transportation Equipment', 'Wood Products', 'Coal', 'Metal', 'Non-Metallic Minerals', 'Wine Bar', 'Sports Bar', 'Hotel Lounge', 'Bar', 'Breweries', 'Internet Cafes', 'Nightlife', 'Strip Club', 'Night Clubs', 'Karaoke', 'Jazz and Blues Cafe', 'Hookah Lounges', 'Adult Entertainment', 'Boat', 'Bus Stations', 'Car and Truck Rentals', 'Charter Buses', 'Cruises', 'Heliports', 'Rail', "Women's Store", 'Swimwear', 'Shoe Store', "Men's Store", 'Lingerie Store', "Kids' Store", 'Boutique', 'Accessories Store', 'Monuments and Memorials', 'Historic Sites', 'Gardens', 'Buildings and Structures', 'Rivers', 'Mountains', 'Lakes', 'Forests', 'Beaches', 'Playgrounds', 'Picnic Areas', 'Natural Parks', 'Parks', 'Payroll', 'Tattooing', 'Tanning Salons', 'Spas', 'Skin Care', 'Piercing', 'Massage Clinics and Therapists', 'Manicures and Pedicures', 'Laundry and Garment Services', 'Hair Salons and Barbers', 'Hair Removal', 'Public Transportation Services', 'Transportation Centers', 'Real Estate Development and Title Companies', 'Real Estate Appraiser', 'Real Estate Agents', 'Property Management', 'Corporate Housing', 'Commercial Real Estate', 'Building and Land Surveyors', 'Boarding Houses', 'Apartments, Condos and Houses', 'Rent', 'Athletic Fields', 'Baseball', 'Basketball', 'Batting Cages', 'Boating', 'Campgrounds and RV Parks', 'Canoes and Kayaks', 'Combat Sports', 'Cycling', 'Dance', 'Equestrian', 'Football', 'Go Carts', 'Golf', 'Gun Ranges', 'Gymnastics', 'Gyms and Fitness Centers', 'Hiking', 'Hockey', 'Hot Air Balloons', 'Hunting and Fishing', 'Landmarks', 'Miniature Golf', 'Outdoors', 'Paintball', 'Personal Trainers', 'Race Tracks', 'Racquet Sports', 'Racquetball', 'Rafting', 'Recreation Centers', 'Rock Climbing', 'Running', 'Scuba Diving', 'Skating', 'Skydiving', 'Snow Sports', 'Soccer', 'Sports and Recreation Camps', 'Sports Clubs', 'Stadiums and Arenas', 'Swimming', 'Tennis', 'Water Sports', 'Yoga and Pilates', 'Zoo', 'Temple', 'Synagogues', 'Mosques', 'Churches', 'Rent', 'Restaurants', 'Winery', 'Vegan and Vegetarian', 'Turkish', 'Thai', 'Swiss', 'Sushi', 'Steakhouses', 'Spanish', 'Seafood', 'Scandinavian', 'Portuguese', 'Pizza', 'Moroccan', 'Middle Eastern', 'Mexican', 'Mediterranean', 'Latin American', 'Korean', 'Juice Bar', 'Japanese', 'Italian', 'Indonesian', 'Indian', 'Ice Cream', 'Greek', 'German', 'Gastropub', 'French', 'Food Truck', 'Fish and Chips', 'Filipino', 'Fast Food', 'Falafel', 'Ethiopian', 'Eastern European', 'Donuts', 'Distillery', 'Diners', 'Dessert', 'Delis', 'Cupcake Shop', 'Cuban', 'Coffee Shop', 'Chinese', 'Caribbean', 'Cajun', 'Cafe', 'Burrito', 'Burgers', 'Breakfast Spot', 'Brazilian', 'Barbecue', 'Bakery', 'Bagel Shop', 'Australian', 'Asian', 'American', 'African', 'Afghan', 'Advertising and Marketing', 'Art Restoration', 'Audiovisual', 'Automation and Control Systems', 'Business and Strategy Consulting', 'Business Services', 'Cable', 'Chemicals and Gasses', 'Cleaning', 'Computers', 'Construction', 'Credit Counseling and Bankruptcy Services', 'Dating and Escort', 'Employment Agencies', 'Engineering', 'Entertainment', 'Events and Event Planning', 'Financial', 'Funeral Services', 'Geological', 'Home Improvement', 'Household', 'Human Resources', 'Immigration', 'Import and Export', 'Industrial Machinery and Vehicles', 'Insurance', 'Internet Services', 'Leather', 'Legal', 'Logging and Sawmills', 'Machine Shops', 'Management', 'Manufacturing', 'Media Production', 'Metals', 'Mining', 'News Reporting', 'Oil and Gas', 'Packaging', 'Paper', 'Personal Care', 'Petroleum', 'Photography', 'Plastics', 'Rail', 'Real Estate', 'Refrigeration and Ice', 'Renewable Energy', 'Repair Services', 'Research', 'Rubber', 'Scientific', 'Security and Safety', 'Shipping and Freight', 'Software Development', 'Storage', 'Subscription', 'Tailors', 'Telecommunication Services', 'Textiles', 'Tourist Information and Services', 'Transportation', 'Travel Agents and Tour Operators', 'Utilities', 'Veterinarians', 'Water and Waste Management', 'Web Design and Development', 'Welding', 'Agriculture and Forestry', 'Art and Graphic Design', 'Adult', 'Antiques', 'Arts and Crafts', 'Auctions', 'Automotive', 'Beauty Products', 'Bicycles', 'Boat Dealers', 'Bookstores', 'Cards and Stationery', 'Children', 'Clothing and Accessories', 'Computers and Electronics', 'Construction Supplies', 'Convenience Stores', 'Costumes', 'Dance and Music', 'Department Stores', 'Digital Purchase', 'Discount Stores', 'Electrical Equipment', 'Equipment Rental', 'Flea Markets', 'Florists', 'Fuel Dealer', 'Furniture and Home Decor', 'Gift and Novelty', 'Glasses and Optometrist', 'Hardware Store', 'Hobby and Collectibles', 'Industrial Supplies', 'Jewelry and Watches', 'Luggage', 'Marine Supplies', 'Music, Video and DVD', 'Musical Instruments', 'Newsstands', 'Office Supplies', 'Outlet', 'Pawn Shops', 'Pets', 'Pharmacies', 'Photos and Frames', 'Shopping Centers and Malls', 'Sporting Goods', 'Tobacco', 'Toys', 'Vintage and Thrift', 'Warehouses and Wholesale Stores', 'Wedding and Bridal', 'Wholesale', 'Lawn and Garden', 'Student Aid and Grants', 'Taxes', 'Refund', 'Payment', 'Wire Transfer', 'Venmo', 'Square Cash', 'Square', 'PayPal', 'Dwolla', 'Coinbase', 'Chase QuickPay', 'Acorns', 'Digit', 'Betterment', 'Plaid', 'Internal Account Transfer', 'ACH', 'Billpay', 'Check', 'Credit', 'Debit', 'Deposit', 'Keep the Change Savings Program', 'Third Party', 'Wire', 'Withdrawal', 'Save As You Go', 'Water', 'Sanitary and Waste Management', 'Heating, Ventilating, and Air Conditioning', 'Gas', 'Electric'
            ]

        parent_category_name = [
            'Advertising and Marketing', 'Advertising and Marketing', 'Advertising and Marketing', 'Advertising and Marketing', 'Advertising and Marketing', 'Advertising and Marketing', 'Advertising and Marketing', 'Advertising and Marketing', 'Advertising and Marketing', 'Advertising and Marketing', 'Agriculture and Forestry', 'Agriculture and Forestry', 'Agriculture and Forestry', 'Agriculture and Forestry', 'Air Travel', 'Air Travel', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'Arts and Entertainment', 'ATM', 'ATM', 'ATM', 'ATM', 'ATM', 'Auto Transportation', 'Auto Transportation', 'Auto Transportation', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Automotive', 'Bank Fees', 'Bank Fees', 'Bank Fees', 'Bank Fees', 'Bank Fees', 'Bank Fees', 'Bank Fees', 'Business Services', 'Car Service', 'Car Service', 'Car Service', 'Car Service', 'Check', 'Clothing and Accessories', 'Clothing and Accessories', 'Clothing and Accessories', 'Clothing and Accessories', 'Clothing and Accessories', 'Clothing and Accessories', 'Clothing and Accessories', 'Clothing and Accessories', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Community Services', 'Computers', 'Computers', 'Credit Card', 'Education', 'Education', 'Education', 'Education', 'Education', 'Education', 'Education', 'Education', 'Education', 'Education', 'Education', 'Education', 'Electronics', 'Electronics', 'Electronics', 'Entertainment', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Food Delivery Services', 'Food and Beverage Store', 'Food and Beverage Store', 'Food and Beverage Store', 'Food and Beverage Store', 'Food and Beverage Store', 'Food and Beverage Store', 'Food and Beverage Store', 'Food and Beverage Store', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Departments and Agencies', 'Government Support', 'Government Support', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Home Improvement', 'Interest', 'Interest', 'Loans and Mortgages', 'Loans and Mortgages', 'Lodging', 'Lodging', 'Lodging', 'Lodging', 'Lodging', 'Lodging', 'Lodging', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Mining', 'Mining', 'Mining', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Nightlife', 'Other Travel', 'Other Travel', 'Other Travel', 'Other Travel', 'Other Travel', 'Other Travel', 'Other Travel', 'Outlet', 'Outlet', 'Outlet', 'Outlet', 'Outlet', 'Outlet', 'Outlet', 'Outlet', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Parks', 'Payroll', 'Personal Care', 'Personal Care', 'Personal Care', 'Personal Care', 'Personal Care', 'Personal Care', 'Personal Care', 'Personal Care', 'Personal Care', 'Personal Care', 'Public Transit', 'Public Transit', 'Real Estate', 'Real Estate', 'Real Estate', 'Real Estate', 'Real Estate', 'Real Estate', 'Real Estate', 'Real Estate', 'Real Estate', 'Real Estate', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Religious', 'Religious', 'Religious', 'Religious', 'Rent', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Restaurants', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Service', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Shops', 'Student Aid and Grants', 'Taxes', 'Taxes', 'Taxes', 'Third Party', 'Third Party', 'Third Party', 'Third Party', 'Third Party', 'Third Party', 'Third Party', 'Third Party', 'Savings Apps', 'Savings Apps', 'Savings Apps', 'Third Party', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Transfer', 'Utilities', 'Utilities', 'Utilities', 'Utilities', 'Utilities'
            ]

        grandparent_category_name = [
            'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Travel', 'Travel', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Transportation', 'Transportation', 'Transportation', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Other', 'Transportation', 'Transportation', 'Transportation', 'Transportation', 'Financial', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Financial', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Shopping', 'Shopping', 'Shopping', 'Recreation', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Govt Agencies', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Healthcare', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Financial', 'Financial', 'Financial', 'Financial', 'Travel', 'Travel', 'Travel', 'Travel', 'Travel', 'Travel', 'Travel', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Travel', 'Travel', 'Travel', 'Travel', 'Travel', 'Travel', 'Travel', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Payroll', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Transportation', 'Transportation', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Recreation', 'Other', 'Other', 'Other', 'Other', 'Financial', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Food', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Other', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Shopping', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Financial', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Transfers', 'Utilities', 'Utilities', 'Utilities', 'Utilities', 'Utilities'
            ]
        
        cache = {
            'category_id': category_id,
            'category_name': category_name,
            'parent_category_name': parent_category_name,
            'grandparent_category_name': grandparent_category_name
        }
        
        df = pd.DataFrame(cache)
            
        if debug is True:
            print(df)
        else:
            return df

    def _fetch_transactions_dataframe(self, bank_account_id: str = None, sample_size: int = 1):
        random_list = []
        feature_list = []

        primary_features = [
            'bank_account_id',
            'id', 
            'date', 
            'amount_cents',
            'category_id',
            'created_at',
        ]

        secondary_features = [
            'plaid_transaction_id',
            'merchant_city',
            'merchant_state',
            'lat', 
            'lon',
            'purpose'
        ]

        feature_list = primary_features + secondary_features

        feature_query = ", ".join(feature_list)

        if bank_account_id:
            query_operation = f"""
            SELECT {feature_query}
            FROM plaid_main_transactions
            WHERE bank_account_id = {bank_account_id}
            """
        else:
            while len(random_list) != sample_size:
                random_number = random.randrange(1, 257603)
                
                query_operation = f"""
                SELECT {feature_query}
                FROM plaid_main_transactions
                WHERE bank_account_id = {random_number}
                """
                
                query_fetch = self.handle_query(query_operation, fetchone=True)
                
                if query_fetch is None:
                    pass
                else:
                    if random_number in random_list:
                        pass
                    else:
                        random_list.append(random_number)

            random_query = ", ".join(repr(i) for i in random_list)

            query_operation = f"""
            SELECT {feature_query}
            FROM plaid_main_transactions
            WHERE bank_account_id IN ({random_query})
            """

        query_fetch = self.handle_query(query_operation)

        df = pd.DataFrame(query_fetch, columns=feature_list)

        return df

    def _wrangle_transactions(self, x):
        """Wrangle incoming transaction data."""
        # Prevent SettingWithCopyWarning
        X = x.copy()

        # remove empty or 'None' values
        X.replace('', np.nan, inplace=True)
        X = X.fillna(value=np.nan)

        # test datetime features
        datetime_features = ['date', 'created_at']

        for i in datetime_features:
            X[i] = pd.to_datetime(X[i],
                                format="%m/%d/%Y, %H:%M:%S",
                                errors='raise') 

        # remove duplicate entries !WARNING (may affect resulting table)
        X = X.drop_duplicates(subset='plaid_transaction_id').reset_index(drop=True)
        
        X.rename(columns={'amount_cents':'amount'}, inplace=True)
        X['amount'] = (X['amount'] / 100).round(2)
        
        # insert category data
        df = self._handle_category_features()
        
        X = pd.merge(X, df, on='category_id')

        return X

    def _fetch_accounts_dataframe(self, bank_account_id: str = None, sample_size: int = 1):
        random_list = []
        feature_list = []
        
        primary_features = [
            'id',
            'current_balance_cents',
            'created_at',
            'updated_at',
            'name',
            'account_type',
            'available_balance_cents',
            'last_balance_update_at',
            'plaid_state',
            'initial_balance_cents',
            'main_saving'
        ]

        secondary_features = [
            'account_subtype'
        ]
        
        feature_list = primary_features + secondary_features

        feature_query = ", ".join(feature_list)

        if bank_account_id:
            query_operation = f"""
            SELECT {feature_query}
            FROM bank_accounts
            WHERE id = {bank_account_id}
            """
        else:
            for _ in range(sample_size):
                random_list.append(random.randrange(1, 257603))

            random_query = ", ".join(repr(i) for i in random_list)

            query_operation = f"""
            SELECT {feature_query}
            FROM bank_accounts
            WHERE id IN ({random_query})
            """

        query_fetch = self.handle_query(query_operation)

        df = pd.DataFrame(query_fetch, columns=feature_list)

        return df
    
    def _wrangle_accounts(self, x):
        X = x.copy()
        
        return X

    def _fetch_requests_dataframe(self):
        feature_list = []
        
        primary_features = [
            'description',
            'state'
        ]
        
        feature_list = primary_features
        
        feature_query = ", ".join(primary_features)

        query_operation = f"""
        SELECT {feature_query}
        FROM emergency_fund_requests
        """

        query_fetch = self.handle_query(query_operation)

        df = pd.DataFrame(query_fetch, columns=feature_list)

        return df
    
    def _wrangle_requests(self, x):
        X = x.copy()
        
        return X

SaverlifeUtility = SaverlifeUtility()


class Visualize():
    """
    Visualize different aspects of user data 
    for SaverLife C Lambda School Labs project
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_transactions_df = self.handle_user_transaction_data()
        self.transaction_time_series_df = self.handle_transaction_timeseries_data()

    def handle_user_transaction_data(self):
        """
        Helper method to filter user data from SaverLife DB 
        """
        df = SaverlifeUtility._generate_dataframe(bank_account_id=self.user_id, table='transactions')
        return df

    def handle_transaction_timeseries_data(self):
        """
        Helper method to clean transaction time series data
        """
        self.transactions_time_series_df = self.user_transactions_df.sort_values("date")
        self.transactions_time_series_df["amount"] = self.transactions_time_series_df["amount"].astype(int)
        self.transactions_time_series_df["formatted_date"] = self.transactions_time_series_df.date.dt.strftime('%Y-%m-%d')
        self.transactions_time_series_df.sort_values("formatted_date", ascending=False, inplace=True)
        return self.transactions_time_series_df

    def handle_resampling_transaction_timeseries_df(self, offset_string):
        """
        Helper method to resample transaction timeseries data
        to a user-specified time frequency
        Args:
            frequency: a pandas DateOffset, Timedelta or str
                See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 
                for more on dateoffset strings
        Returns:
            resampled_transaction_timeseries
        Usage:
        # Resample to weekly sum
        >>> resampled_data = self.handle_resampling_transaction_timeseries_df(offset_string="W")
        """
        self.resampled_transaction_timeseries = self.transactions_time_series_df.copy()
        self.resampled_transaction_timeseries["date"] = pd.to_datetime(self.resampled_transaction_timeseries["date"])
        self.resampled_transaction_timeseries.set_index("date", inplace=True)
        return self.resampled_transaction_timeseries.groupby("category_name").resample(offset_string).sum().reset_index()
    
    def handle_resampling_transaction_timeseries_df_parent_categories(self, offset_string):
            """
            Helper method to resample transaction timeseries data
            to a user-specified time frequency
            Args:
                frequency: a pandas DateOffset, Timedelta or str
                    See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 
                    for more on dateoffset strings
            Returns:
                resampled_transaction_timeseries
            Usage:
            # Resample to weekly sum
            >>> resampled_data = self.handle_resampling_transaction_timeseries_df(offset_string="W")
            """
            self.resampled_transaction_timeseries = self.transactions_time_series_df.copy()
            self.resampled_transaction_timeseries["date"] = pd.to_datetime(self.resampled_transaction_timeseries["date"])
            self.resampled_transaction_timeseries.set_index("date", inplace=True)
            return self.resampled_transaction_timeseries.groupby("parent_category_name").resample(offset_string).sum().reset_index()[["parent_category_name","date","amount"]]

    def return_all_transactions_for_user(self):
        """
        Plotly Table Object of all transactions for a user
        Usage:
        # Instantiate the class
        >>> visualize = Visualize(user_id=4923847023975)
    
        # Plotly table of all transactions for a single user
        >>> visualize.return_all_transactions_for_user()
        """
        fig = go.Figure(data=[go.Table(header=dict(values=["Date", 
                                                           "Amount", 
                                                           "Category",
                                                           "Parent Category",
                                                           "Grandparent Category"],
                                                   fill_color='lightgray',
                                                   align='left'),
                                       cells=dict(values=[self.transaction_time_series_df.formatted_date, 
                                                          self.transaction_time_series_df.amount, 
                                                          self.transaction_time_series_df.category_name,
                                                          self.transaction_time_series_df.parent_category_name,
                                                          self.transaction_time_series_df.grandparent_category_name],
                                                  fill_color='whitesmoke',
                                                  align='left'))])
        fig.update_layout(title_text="Transactions: User {}".format(self.user_id),
                          title_font_size=30)
        return fig.to_json()

    def categorized_bar_chart_per_month(self):
        """
        Plotly Bar Chart Object of monthly sum transactions for a user
        Usage:
        # Instantiate the class
        >>> visualize = Visualize(user_id=4923847023975)
    
        # Plotly bar chart of monthly sum transactions
        >>> visualize.categorized_bar_chart_per_month()
        """
        def helper_function_for_trace_visibility(len_array, i):
            intermediate_array = [False] * len_array
            intermediate_array[i] = True
            return intermediate_array
        self.monthly_sum_transactions_time_series_df = self.handle_resampling_transaction_timeseries_df("M").sort_values("date")
        self.monthly_sum_transactions_time_series_df.drop(columns=["bank_account_id","id","lat","lon"], inplace=True)
        self.monthly_sum_transactions_time_series_df = self.monthly_sum_transactions_time_series_df.loc[self.monthly_sum_transactions_time_series_df['amount'] != 0]
        months_of_interest = self.monthly_sum_transactions_time_series_df.date.dt.strftime('%Y-%m').unique().tolist()
        
        self.monthly_sum_transactions_time_series_df['label'] = self.monthly_sum_transactions_time_series_df['amount'].apply(lambda x: 'outflow' if x >= 0 else 'inflow')
        self.monthly_sum_transactions_time_series_df = self.monthly_sum_transactions_time_series_df.sort_values(['amount'], ascending=True)
        colorsIdx = {'inflow': '#C01089', 'outflow': '#4066B0'}
        
        length_of_interest = len(months_of_interest)
        list_of_monthly_dfs = []
        for month in months_of_interest:
            list_of_monthly_dfs.append(self.monthly_sum_transactions_time_series_df[self.monthly_sum_transactions_time_series_df.date.dt.strftime('%Y-%m') == month])

        fig = go.Figure()

        for i in range(len(list_of_monthly_dfs)-1):
            cols = list_of_monthly_dfs[i]['label'].map(colorsIdx)
            fig.add_trace(go.Bar(y=list(list_of_monthly_dfs[i].category_name), 
                                 x=list(list_of_monthly_dfs[i].amount), 
                                 name=str(list_of_monthly_dfs[i].date.dt.strftime('%Y-%m').iloc[0]), 
                                 visible=False, 
                                 orientation='h',
                                 marker=dict(color=cols)))
        cols = list_of_monthly_dfs[-1]['label'].map(colorsIdx)
        fig.add_trace(go.Bar(y=list(list_of_monthly_dfs[-1].category_name), 
                             x=list(list_of_monthly_dfs[-1].amount), 
                             name=str(list_of_monthly_dfs[-1].date.dt.strftime('%Y-%m').iloc[0]), 
                             visible=True, 
                             orientation='h',
                             marker=dict(color=cols)))

        fig.update_layout(
            font_family='Arial',
            template='simple_white',
            height=800)
        
        fig.update_layout(
            updatemenus=[
                dict(active=length_of_interest-1, buttons=list([
                        dict(label=months_of_interest[i],
                             method="update",
                             args=[{"visible": helper_function_for_trace_visibility(length_of_interest, i)},
                                   {"annotations": []}]) for i in range(length_of_interest)]))])

        return fig.to_json()
    
    def next_month_forecast(self, model="kNeighbors"):
        """
        Forecast next month's transactions based on historical transactions
        Caveats:
            Only forecasts for parent_categories for which 
            there are at least 12 months of observations available
        Returns:
            Dictionary of forecasts, with parent_category_name 
            as key and forecasted amount_cents as value
        
        Usage:
            # Instantiate the class
        >>> visualize = Visualize(user_id=45153)
    
        # Forecast transactiosn for next month
        >>> visualize.next_month_forecast()
        """
        # Resample to monthly sum per parent_category_name
        self.monthly_parent_category_total = self.handle_resampling_transaction_timeseries_df_parent_categories("M")
        # Filter for parent_categories with at least 12 months of data
        self.df12 = self.monthly_parent_category_total[self.monthly_parent_category_total['parent_category_name'].map(self.monthly_parent_category_total['parent_category_name'].value_counts()) > 12]
        # Container to store forecasting results
        self.forecasting_results = {}
        # Loop through each parent category and forecast month ahead with Naive Baseline
        for parent_cat in self.df12.parent_category_name.unique().tolist():
            # Select relevant transaction data for training the model
            y = self.df12[self.df12.parent_category_name == parent_cat]["amount"]
            # Set forecasting horizon
            fh = np.arange(len(y)) + 1 
            # Initialize a forecaster, seasonal periodicity of 12 (months per year)   
            if model == "Naive":
                forecaster = NaiveForecaster(strategy="seasonal_last", sp=12)
            else:
                regressor = KNeighborsRegressor(n_neighbors=1)
                forecaster = ReducedRegressionForecaster(regressor=regressor, window_length=12, strategy="recursive")        
            # Fit forecaster to training data
            forecaster.fit(y)
            # Forecast prediction to match size of forecasting horizon
            y_pred = forecaster.predict(fh)
            # Store results in a dictionary
            self.forecasting_results[parent_cat] = y_pred.values[0]
        # Return the results for use in other parts of app
        return self.forecasting_results


@router.post('/dev/requesttesting', tags=["Graph"])
async def read_user(payload: GraphRequest):
    """
    Returns a visual table or graph according to input parameters.
    """

    user_id = f"{request.user_id}"
    graph_type = f"{request.graph_type}"
    start_month = f"{request.start_month}"
    end_month = f"{request.end_month}"

    return {
        'message': 'The payload sent in a 200 response.',
        'payload': {
            'user_id': user_id,
            'graph_type': graph_type,
            'optional[start_month]': start_month,
            'optional[end_month]': end_month
        }
    }


@router.post('/dev/requestvisual', tags=["Graph"])
async def read_user(payload: GraphRequest):
    """
    Returns a visual table or graph according to input parameters.
    """
    SaverlifeVisual = Visualize(user_id=payload.user_id)
    
    if SaverlifeVisual.user_transactions_df.size > 0:
        pass
    else: 
        return {
            'details': [
                {
                    'loc': [
                        'internal',
                        'dataframe'
                    ],
                    'msg': 'dataframe size 0, possible invalid user_id',
                    'type': 'internal'
                }
            ]
        }
    
    def _parse_graph(graph_type=payload.graph_type):
        if graph_type == 'TransactionTable':
            fig = SaverlifeVisual.return_all_transactions_for_user()
        if graph_type == 'CategoryBarMonth':
            fig = SaverlifeVisual.categorized_bar_chart_per_month()
        
        return fig

    return _parse_graph()


@router.get('/dev/forecast/', tags=['Forecast'])
async def return_forecast(payload: Optional[User] = None, user_id: Optional[str] = None):
    """
    Returns a dictionary forecast.
    """
    if payload:
        SaverlifeVisual = Visualize(user_id=payload.user_id)
    else:
        SaverlifeVisual = Visualize(user_id=user_id)

    forecast = SaverlifeVisual.next_month_forecast()

    cache = {}
    for key, value in forecast.items():
        cache[str(key)] = int(value)
        
    if forecast:
        return cache
    else: 
        return {
            'details': [
                {
                    'loc': [
                        'internal',
                        'model'
                    ],
                    'msg': 'dictionary size 0, possible too few model observations.',
                    'doc': {
                        'description': "Forecast next month's transactions based on historical transactions.",
                        'caveats': "Only forecasts for parent_categories for which there are at least 12 months of observations available",
                        'returns': "Dictionary of forecasts, with parent_category_name as key and forecasted amount_cents as value"
                    },
                    'type': 'internal'
                }
            ]
        }