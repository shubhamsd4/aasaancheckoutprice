import streamlit as st
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Aasaan Checkout Price Calculator", page_icon=":tada:", layout="wide")


#Load Assets
#aasaan_logo = Image.open("../Images/aasaan_logo.png")

#---Functions---
#Indian format
def convert_to_indian_currency(number):
    s, *d = str(number).partition(".")
    r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    return '₹' + "".join([r] + d)


#Estimated Yearly Revenue 
def est_yearly_revenue(txn, AOV):
    return txn*AOV*12

#Incremental Revenue Percentage Estimation
def incr_rev_perc(revenue):
    if revenue<500000:
        return 0.30
    elif revenue<1000000:
        return 0.20
    elif revenue<2500000:
        return 0.10
    else:
        return 0.05

#Incremental Revenue Estimation
def incr_rev(revenue, incr_rev_perc):
    return revenue*incr_rev_perc

#Months to breakeven
def breakeven(aasaan_cost, incr_rev):
    roi = incr_rev/aasaan_cost
    return 12/roi

#Prepaid Aasaan Price Calculation
def aasaan_prepaid(plan):
    if plan == 'Quarterly':
        return 60000
    elif plan =="Half-yearly":
        return 50000
    elif plan=="Yearly":
        return 35000

#Postpaid Aasaan Base Percentage Price Calculation
class AasaanPostPaidBasePriceCalculation:
    def __init__(self,txn_details,base_details, base_price_comp, no_of_slabs):
       self.txn_details = txn_details
       self.base_details = base_details  
       self.base_price_comp = base_price_comp
       self.no_of_slabs = no_of_slabs  
    
    def aasaan_postpaid_base_price(self):
        price = float(self.txn_details[0])*float(self.base_details[0])
        if(int(self.no_of_slabs)>1):
            for i in range(1, int(self.no_of_slabs)):
                price = price + (float(self.txn_details[i])-float(self.txn_details[i-1]))*float(self.base_details[i])
        price = 12*price
        return price 
        
    def aasaan_postpaid_base_price_comp(self):
        price_comp = float(self.txn_details[0])*float(self.base_price_comp[0])
        if(int(self.no_of_slabs)>1):
            for i in range(1, int(self.no_of_slabs)):
                price_comp = price_comp + (float(self.txn_details[i])-float(self.txn_details[i-1]))*float(self.base_price_comp[i])
        price_comp = 12*price_comp 
        return price_comp


#Postpaid Aasaan Base Price Price Calculation
class AasaanPostPaidBasePercCalculation:
    def __init__(self,txn_details,base_details,base_comp_details, aov,no_of_slabs):
       self.txn_details = txn_details
       self.base_details = base_details
       self.base_comp_details = base_comp_details  
       self.aov = aov
       self.no_of_slabs = no_of_slabs  
    
    def aasaan_postpaid_base_perc(self):
        price = float(self.txn_details[0])*float(self.base_details[0])*0.01*float(self.aov)
        if(int(self.no_of_slabs)>1):
            for i in range(1, int(self.no_of_slabs)):
                price = price + (int(self.txn_details[i])-int(self.txn_details[i-1]))*float(self.base_details[i])*0.01*float(self.aov)
        price = 12*price
        return price

    def aasaan_postpaid_comp_base_perc(self):
        price_comp = float(self.txn_details[0])*float(self.base_comp_details[0])*0.01*float(self.aov)
        if(int(self.no_of_slabs)>1):
            for i in range(1, int(self.no_of_slabs)):
                price_comp = price_comp + (int(self.txn_details[i])-int(self.txn_details[i-1]))*float(self.base_comp_details[i])*0.01*float(self.aov)
        price_comp = 12*price_comp
        return price_comp
 


class CompetitorPriceCalculation:
    def __init__(self, txn, AOV):
        self.txn = txn
        self.AOV = AOV

    #Xpresslane Price Calculation
    def xpresslane_price(self):
        xpresslane_txn_perc = 0.8
        return round(12*self.txn*self.AOV*xpresslane_txn_perc*0.01,2)

    #Nimbl Price Calculation
    def nimbl_price(self):
        nimbl_txn_perc = 2.1
        return round(12*self.txn*self.AOV*nimbl_txn_perc*0.01, 2)

    #GoKwik Price Calculation
    def gokwik_price(self):
        gokwik_txn_perc = 2.3
        min_gaurantee_fee = 15000
        return round(12*max(min_gaurantee_fee, self.txn*self.AOV*gokwik_txn_perc*0.01),2)

    #Shopflo Price Calculation
    def shopflo_price(self):
        installation_fee = 10000
        monthly_fee_slab2 = 8223
        monthly_fee_slab3 = 8223*2
        shopflo_slab1_txn_perc = 2.5
        shopflo_slab2_txn_perc = 1
        shopflo_slab3_txn_perc = 0.5
        shopflo_slab1 = 500000/self.AOV
        shopflo_slab2 = 1600000/self.AOV
        if self.txn <= shopflo_slab1:
            return installation_fee + 8*self.txn*self.AOV*shopflo_slab1_txn_perc*0.01
        if self.txn > shopflo_slab1 and self.txn <= shopflo_slab2:
            return installation_fee + 8*(shopflo_slab1*self.AOV*shopflo_slab1_txn_perc*0.01 + (self.txn - shopflo_slab1)*self.AOV*shopflo_slab2_txn_perc*0.01) + 8*monthly_fee_slab2
        if self.txn > shopflo_slab2:
            return installation_fee + 8*(shopflo_slab1*self.AOV*shopflo_slab1_txn_perc*0.01 + (shopflo_slab2 - shopflo_slab1)*self.AOV*shopflo_slab2_txn_perc*0.01 + (self.txn - shopflo_slab2)*self.AOV*shopflo_slab3_txn_perc*0.01) + 8*monthly_fee_slab3


#---Function to get comp. dictionary---
def comp_price_dict(monthly_txn, aov,selected_competitors):
    comp_price_calculator = CompetitorPriceCalculation(float(monthly_txn), float(aov))
    if 'Xpresslane' in selected_competitors:
        competitor_prices['Xpresslane'] = comp_price_calculator.xpresslane_price()
    if 'Nimbl' in selected_competitors:
        competitor_prices['Nimbl'] = comp_price_calculator.nimbl_price()
    if 'GoKwik' in selected_competitors:
        competitor_prices['GoKwik'] = comp_price_calculator.gokwik_price()
    if 'Shopflo' in selected_competitors:
        competitor_prices['Shopflo'] =  comp_price_calculator.shopflo_price()
    return competitor_prices

def pricingModelSelector(monthly_txn, aov,txn_nature):
    if aov<=1000:
        if monthly_txn*aov*0.25*0.01*12 <=35000:
            return "Prepaid",0
        else:
            if txn_nature == "Constant": 
                return "Postpaid Base Percentage",0
            else:
                return "Postpaid Base Percentage",1

    else:
        if monthly_txn*1.75*12 <=35000:
            return "Prepaid",0
        else:
            if txn_nature == "Constant": 
                return "Postpaid Base Price",0
            else:
                return "Postpaid Base Price",1
     
    



# ---Logo & Heading Section---
#st.markdown("<p style='text-align: center;'><img src='/Users/shubhamsd4/Documents/Work/Aasaan Price Calculator/Images/aasaan_logo.png'></p>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'>Aasaan Checkout Price Calculator</h1>", unsafe_allow_html=True)



#---Intro Section --- 
with st.container():
    st.subheader("Hi there :wave:")
    st.write("Aasaan Checkout Price Calculator is a tool for the Sales Executives (that is you :smiley:) so that you can show our prospective merchants about the price they'd have to pay for the current revenue they're generating and also compare it with Aasaan's competitors to show them we are way better in terms of pricing as well apart from the features :sunglasses:. All you have to do is:")
    st.markdown(
        """
        1. Choose the competitors you want to compare against
        2. Ask our prospective merchants what their Avg. Order Value, their monthly transactions and nature of their transactions
        3. Input the pricing details on the basis of the pricing model suggested
        """)

st.write('<style>.my-input { width: 300px; }</style>', unsafe_allow_html=True)

#--Checkbox for UAE-- 
st.subheader("Select the below checkbox for UAE clients")
country =['India','UAE']
country_dropdown = st.selectbox("Select Target Region", country)

if country_dropdown == 'India':
    #--Choose Competitor ---
    with st.container():
        st.write("---")
        st.subheader("Competitor Comparision")
        competitor_names = ['GoKwik', 'Shopflo','Xpresslane','Nimbl']
        selected_competitors = st.multiselect("Select Competitors to compare with", competitor_names)
        #update_competitor = st.button("Update Competitors")
        competitor_prices = {}


    #--Pricing Model Selector---
    with st.container():
        st.write("---")
        st.subheader("Pricing Model Selector")  

        #Taking the inputs aov,  txn and distribution details for comp. benchmarking
        left_column, right_column = st.columns(2)
        with left_column:
            aov_check = st.text_input("Avg. Order Value (in Rs.)", key='my_input')

        with right_column:
            monthly_txn_check= st.text_input("Avg. Transactions per Month", key='my_input1')

        txn_nature = st.radio("Select the nature of the monthly transactions over the year", ["Constant", "Fluctuating"], key="txn_nature_key")

        if aov_check and monthly_txn_check:
            priceModule,isTiered = pricingModelSelector(int(monthly_txn_check), float(aov_check),txn_nature)
        else:
            priceModule = 0

        getPricingModel = st.button("Get Pricing Model", key="getPMButton")


    #---Prepaid ---
    with st.container():
        st.write("---")
        if priceModule == "Prepaid":
                st.subheader("Prepaid Pricing Model")  

                #Taking the inputs aov and txn details for comp. benchmarking
                left_column, right_column = st.columns(2)
                with left_column:
                    aov = st.text_input("Avg. Order Value (in Rs.)", value=aov_check)
                with right_column:
                    monthly_txn = st.text_input("Avg. Transactions per Month", value = monthly_txn_check)

                est_revenue_prepaid = est_yearly_revenue(int(monthly_txn), float(aov)) 
                incr_revenue_perc_prepaid = incr_rev_perc(est_revenue_prepaid)
                incr_revenue_prepaid = incr_rev(est_revenue_prepaid, incr_revenue_perc_prepaid) 


                #Subscription Plan Dropdown 
                subscription_plans_options = ['Quarterly', 'Half-yearly', 'Yearly']
                selected_subscription_plan = st.selectbox("Select the Prepaid Subscription Type", subscription_plans_options, key='prepaid_sub_plan')
                prepaid_button = st.button("Calculate Price")

                #Competitor Function Values   
                if aov and monthly_txn:
                    competitor_prices = comp_price_dict(monthly_txn, aov,selected_competitors)
                aasaan_column, comp_column = st.columns(2)
                if prepaid_button:
                    with aasaan_column:
                        st.metric("Aasaan Yearly Cost",convert_to_indian_currency(aasaan_prepaid(selected_subscription_plan)))
                        st.metric("Yearly Incremental Revenue", convert_to_indian_currency(incr_revenue_prepaid))
                        st.metric("Months to breakeven", round(breakeven(aasaan_prepaid(selected_subscription_plan), incr_revenue_prepaid),2))
                    with comp_column:
                        for key in competitor_prices.keys():
                            st.metric(key, convert_to_indian_currency(competitor_prices[key]))
        else:
            st.empty()


        #---Postpaid Base Price---
        if priceModule == "Postpaid Base Price":    
            st.subheader("Postpaid Pricing Model: Base Price")
            if isTiered:
                st.write("Tiered")
                no_of_slabs = st.text_input("Enter number of slabs")
                st.button("Get Slabs")
            else:
                st.write("Non-Tiered")
                no_of_slabs = 1
            aov_bprice = st.text_input("Avg. Order Value (in Rs.)", value=aov_check, key="AOV base price")
            max_txn = []
            base_price=[]
            base_price_comp = []
            left_column, right_column = st.columns(2)
            if no_of_slabs:
                if int(no_of_slabs)<=5 and int(no_of_slabs)>0:
                    for i in range(int(no_of_slabs)):
                        with left_column:
                            st.text(f"Slab {i+1}")
                            if no_of_slabs ==1:
                                max_txn.append(st.text_input("Maximum number of transactions per month",value= monthly_txn_check, key = f"key{i}"))
                            else:
                                max_txn.append(st.text_input("Maximum number of transactions per month",key = f"key{i}"))
                        with right_column:
                            base_price.append(st.number_input("Price per transaction(in Rs.)", key = f"key{i+10}"))
                            base_price_comp.append(st.number_input("Competitor Price per transaction(in Rs.)", key = f"key{i+100}"))
                else:
                    st.error("Number of slabs can be from 1-5")
                postpaid_base_price_button = st.button("Calculate Price", key="postpaid base price")

                aasaan_column, comp_column = st.columns(2)
                if postpaid_base_price_button:
                    monthly_txn_bprice = max(max_txn)
                    est_revenue_bprice = est_yearly_revenue(int(monthly_txn_bprice), float(aov_bprice)) 
                    incr_revenue_perc_bprice = incr_rev_perc(est_revenue_bprice)
                    incr_revenue_bprice = incr_rev(est_revenue_bprice, incr_revenue_perc_bprice)

                    postpaid_base_price_obj = AasaanPostPaidBasePriceCalculation(max_txn, base_price, base_price_comp, no_of_slabs)
                    postpaid_baseprice_pricing = postpaid_base_price_obj.aasaan_postpaid_base_price()
                    postpaid_baseprice_comp_pricing = postpaid_base_price_obj.aasaan_postpaid_base_price_comp()
                    with aasaan_column:
                        st.metric("Aasaan Yearly Cost", convert_to_indian_currency(postpaid_baseprice_pricing))
                        st.metric("Yearly Incremental Revenue", convert_to_indian_currency(incr_revenue_bprice))
                        st.metric("Months to breakeven", round(breakeven(postpaid_baseprice_pricing, incr_revenue_bprice),2))
                    with comp_column:
                        st.metric("Competitor", convert_to_indian_currency(postpaid_baseprice_comp_pricing))


                        #st.write(monthly_txn_bprice)
                        #Competitor Function Values   
                        if aov_bprice and monthly_txn_bprice:
                            competitor_prices = comp_price_dict(monthly_txn_bprice, aov_bprice,selected_competitors)


                        for key in competitor_prices.keys():
                            st.metric(key, convert_to_indian_currency(competitor_prices[key]))
        else:
            st.empty()

    #---Postpaid Base Percentage---

        if priceModule =="Postpaid Base Percentage":    
            st.subheader("Postpaid Pricing Model: Base Percentage")
            if isTiered:
                st.write("Tiered")
                no_of_slabs = st.text_input("Enter number of slabs", key="base percentage")
                st.button("Get Slabs", key="base_perc_key")
            else:
                st.write("Non-Tiered")
                no_of_slabs = 1
            aov_bperc = st.text_input("Avg. Order Value (in Rs.)", value=aov_check, key="AOV base percentage")
            max_txn_perc = []
            base_perc=[]
            base_perc_comp = []
            left_column, right_column = st.columns(2)
            if no_of_slabs:
                if int(no_of_slabs)<=5 and int(no_of_slabs)>0:
                    for i in range(int(no_of_slabs)):
                        with left_column:
                            st.text(f"Slab {i+1}")
                            if no_of_slabs ==1:
                                max_txn_perc.append(st.text_input("Maximum number of transactions per month", value=monthly_txn_check, key = f"key{i+20}"))
                            else:
                                max_txn_perc.append(st.text_input("Maximum number of transactions per month",key = f"key{i+20}"))
                        with right_column:
                            base_perc.append(st.number_input("Percentage per transaction amount(in %)", key = f"key{i+50}"))
                            base_perc_comp.append(st.number_input("Competitor Percentage per transaction amount(in %)", key = f"key{i+150}"))
                else:
                    st.error("Number of slabs can be from 1-5")

                postpaid_base_perc_button = st.button("Calculate Price", key="postpaid base perc")

                aasaan_column, comp_column = st.columns(2)
                if postpaid_base_perc_button and aov_bperc:
                    monthly_txn_bperc = max(max_txn_perc)
                    est_revenue_bperc = est_yearly_revenue(int(monthly_txn_bperc), float(aov_bperc)) 
                    incr_revenue_perc_bperc = incr_rev_perc(est_revenue_bperc)
                    incr_revenue_bperc = incr_rev(est_revenue_bperc, incr_revenue_perc_bperc)

                    postpaid_base_perc_obj = AasaanPostPaidBasePercCalculation(max_txn_perc, base_perc, base_perc_comp, aov_bperc, no_of_slabs)
                    postpaid_baseperc_pricing = postpaid_base_perc_obj.aasaan_postpaid_base_perc()
                    postpaid_baseperc_comp_pricing = postpaid_base_perc_obj.aasaan_postpaid_comp_base_perc()
                    with aasaan_column:
                        st.metric("Aasaan Yearly Cost", convert_to_indian_currency(postpaid_baseperc_pricing))
                        st.metric("Yearly Incremental Revenue", convert_to_indian_currency(incr_revenue_bperc))
                        st.metric("Months to breakeven", round(breakeven(postpaid_baseperc_pricing, incr_revenue_bperc),2))
                    with comp_column:
                        st.metric("Competitor", convert_to_indian_currency(postpaid_baseperc_comp_pricing))

                        monthly_txn_bperc = max(max_txn_perc)

                        #Competitor Function Values   
                        if aov_bperc and monthly_txn_bperc:
                            competitor_prices_bperc = comp_price_dict(monthly_txn_bperc, aov_bperc, selected_competitors)

                        for key in competitor_prices_bperc.keys():
                            st.metric(key, convert_to_indian_currency(competitor_prices_bperc[key])) 
        else:
            st.empty()

            

