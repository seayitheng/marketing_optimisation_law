from conf import Logger
from conf import Config
from typing import List, Dict
from src.optimisation_model.input_handler import InputHandler
import collections


class Cluster:
    def __init__(self, cluster:str, customer_count:int):
        self.cluster = cluster
        self.customer_count = customer_count

    def __str__(self):
        return f"Cluster: {self.cluster} has {self.customer_count} of customers"


class Product:
    def __init__(self, product_type:str, product_count:int):
        self.product_type = product_type
        self.product_count = product_count

    def __str__(self):
        return f"Product: {self.product_type} has count of {self.product_count}"


class Customer:
    def __init__(self, name:str, customer_cluster_list:list, customer_cluster_product_list:list):
        self.name = name
        self.customer_cluster_list = customer_cluster_list
        self.customer_cluster_product_list = customer_cluster_product_list

    def __str__(self):
        return f"Customer: {self.name} with customer_cluster_list {self.customer_cluster_list} and products {self.customer_cluster_product_list}"


class Preprocessing():
    """
    This class is intended to pre-process the data,
    such that it can be ingested by the optimisation 
    model class.
    """
    
    def __init__(self, api_data=None):
        self._logger = Logger().logger
        self.cluster_list: List[Cluster] = []
        self.product_list: List[Product] = []
        self.product_cost:Dict = None
        self.product_profit:Dict = None
        self.customer_list: List[Customer] = []
        self.customer_cost:Dict = None
        self.customer_profit:Dict = None
        self.api_data = api_data
        self.budget = Config.OPT_PARAMS['budget']
        self.roi = (Config.OPT_PARAMS['roi'] - 100)/100
        if self.api_data is None:
            self.__process_cluster()
            self.__process_product()
            self.__process_customer()
            self.__process_product_cost()
            self.__process_product_profit()
        else:
            self.__process_json()
            
        
    def __process_json(self):
        #cluster_df = collections.ChainMap(*self.api_data['cluster'])
        cluster_df = self.api_data['cluster']
        for dic in cluster_df:
            thisCluster = Cluster(dic['Cluster'], float(dic['Count']))
            self.cluster_list.append(thisCluster)

        product = self.api_data['product']
        for dic in product:
            thisProduct = Product(dic['Product_Type'], float(dic['Count']))
            self.product_list.append(thisProduct)
        
        cost = self.api_data['cost']
        self.product_cost = {}
        for dict in cost:
            p=(dict['Product_Type_Cost'])
            for k,v in dict.items():
                if k !='Product_Type_Cost':
                    self.product_cost[k, p] = float(v)
        #{(i['Product_Type_Cost'],k):v for k,v in i.items() for i in l if k!='Product_Type_Cost'}

        profit = self.api_data['profit']
        self.product_profit = {}
        for dict in profit:
            p=(dict['Product_Type_Profit'])
            for k,v in dict.items():
                if k !='Product_Type_Profit':
                    self.product_profit[k, p] = float(v)

        cust_cost_profit = self.api_data['cust_cost_profit']
        self.customer_cost = {}
        for dic in cust_cost_profit:
            self.customer_cost[dic['Cluster'], dic['Customer'], dic['Product']] = float(dic['Cost'])
            thisCustomer = Customer(dic['Customer'], (dic['Cluster'], dic['Customer']), [dic['Cluster'], dic['Customer'], dic['Product']])
            self.customer_list.append(thisCustomer)

        self.customer_profit = {}
        for dic in cust_cost_profit:
            self.customer_profit[dic['Cluster'], dic['Customer'], dic['Product']] = float(dic['Profit'])
        self.budget = self.api_data['budget']
        self.roi = (self.api_data['roi'] - 100)/100

    def __process_cluster(self):
        """
        This function processes the cluster dataset
        and save the data into the cluster list.
        """
        df_cluster = InputHandler.get_data_cluster()
        for _, row in df_cluster.iterrows():
            thisCluster = Cluster(*row)
            self.cluster_list.append(thisCluster)
        self._logger.debug("[DataProcessing] Processed data for Cluster Data.")
            
    def __process_product(self):
        """
        This function processes the product dataset
        and save the product details into the product list.
        """
        df_product = InputHandler.get_data_product()
        for _, row in df_product.iterrows():
            thisProduct = Product(*row)
            self.product_list.append(thisProduct)
        self._logger.debug("[DataProcessing] Processed data for Product Data.") 
    
    def __process_product_cost(self):
        """product cost by cluster"""
        cost_df = InputHandler.get_data_product_cost()
        keys = list(cost_df.loc[:, 'Unnamed: 0'])
        cost_df = cost_df.iloc[:, 1:]
        self.product_cost = {}
        for i,l1 in enumerate(keys):
            for j,l2 in enumerate(cost_df):
                self.product_cost[l1, l2] = cost_df.iloc[i, j]
        self._logger.debug("[DataProcessing] Processed data for Product Cost.")
        
    def __process_product_profit(self):
        """product cost by cluster"""
        profit_df = InputHandler.get_data_product_profit()
        keys = list(profit_df.loc[:, 'Unnamed: 0'])
        profit_df = profit_df.iloc[:, 1:]
        self.product_profit = {}
        for i,l1 in enumerate(keys):
            for j,l2 in enumerate(profit_df):
                self.product_profit[l1, l2] = profit_df.iloc[i, j]
        self._logger.debug("[DataProcessing] Processed data for Product Profit.")

    def __process_customer(self):
        """
        This function processes the customer dataset
        and save the customer details into the customer list.
        """
        df_customer = InputHandler.get_data_customers()
        cost = df_customer[['Cluster', 'Customer', 'Product', 'Cost']]
        cost = cost.pivot(index=['Cluster', 'Customer'], columns='Product', values='Cost').reset_index()            
        profit = df_customer[['Cluster', 'Customer', 'Product', 'Profit']]
        profit = profit.pivot(index=['Cluster', 'Customer'], columns='Product', values='Profit').reset_index()
        ### cost dictionary
        key_cost = cost[['Cluster','Customer']]
        dict_key_cost = {}
        for _, row in key_cost.iterrows():
            dict_key_cost[row[1]] = row[0]
        cost_df = cost.iloc[:, 2:]
        self.customer_cost = {}
        i = 0
        for customer, cluster in dict_key_cost.items():
            for index, product in enumerate(cost_df):
                self.customer_cost[cluster, customer, product] = cost_df.iloc[i, index]
                thisCustomer = Customer(customer, (cluster, customer), [cluster, customer, product])
                self.customer_list.append(thisCustomer)
            i = i + 1
        ### profit dictionary
        self.customer_profit = {}
        profit_df = profit.iloc[:, 2:]
        i = 0
        for customer, cluster in dict_key_cost.items():
            for index, product in enumerate(profit_df):
                self.customer_profit[cluster, customer, product] = profit_df.iloc[i, index]
            i = i + 1
        self._logger.debug("[DataProcessing] Processed data for Customer Data, Cost & Profit.")
    

    @property
    def cluster_data(self):
        return self.cluster_list
    
    @property
    def product_data(self):
        return self.product_list
    
    @property
    def customer_data(self):
        return self.customer_list
        

if __name__ == "__main__":
    Preprocessing()
        
        
        
    