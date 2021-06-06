from base import Logger
from conf import Config
import pandas as pd
from base.data_connectors import PandasFileConnector
from pathlib import Path

class Postprocessing(object):
     
    def __init__(self, tactical_model, operational_model, export=False):
        self._logger = Logger().logger
        self.tactical_model = tactical_model
        self.operational_model = operational_model
        self._result_list = []
        self.money_df, self.clus_prod_selected = self.__product_allocation()
        self.cust_money_df, self.clus_cust_prod_selected = self.__offer_allocation()

        # Converting results into a JSON format
        self.compiled_json_results = {
            "tactical_expected_money": self.money_df.to_dict(orient='records'),
            "cluster_product_assignment_data": self.clus_prod_selected.to_dict(orient='records'),
            "operational_expected_money": self.cust_money_df.to_dict(orient='records'),
            "cluster_product_customer_assignment_data": self.clus_cust_prod_selected.to_dict(orient='records'),
        }

        # Converting results into a JSON format
        if export:
            self._logger.debug("[Data Export to CSV] initiated...")
            PandasFileConnector.save(self.money_df, Path(Config.MODEL_INPUTOUTPUT['export_settings'].get('csv')['export_filepath'], "Tactical_Expected_Money.csv"))
            PandasFileConnector.save(self.clus_prod_selected, Path(Config.MODEL_INPUTOUTPUT['export_settings'].get('csv')['export_filepath'], "Cluster_Product_Assignment_data.csv"))
            PandasFileConnector.save(self.cust_money_df, Path(Config.MODEL_INPUTOUTPUT['export_settings'].get('csv')['export_filepath'], "Operational_Expected_Money.csv"))
            PandasFileConnector.save(self.clus_cust_prod_selected, Path(Config.MODEL_INPUTOUTPUT['export_settings'].get('csv')['export_filepath'], "Cluster_Product_Customer_Assignment_Data.csv"))
    
    def __product_allocation(self):
        self._logger.debug("[PostProcessing] Optimal Products' allocation detail is as such...")
        total_expected_profit = 0
        total_expected_cost = 0
        clus_prod_selected = pd.DataFrame()
        money_df = pd.DataFrame()
        for cluster, product in self.tactical_model.cp:
            append_row = pd.DataFrame({
                'cluster': cluster,
                'product': product,
                'Count': self.tactical_model.y[cluster, product].value if (self.tactical_model.y[cluster, product].value)> 1e-6 else 0,
                'Cost': self.tactical_model.expected_cost[cluster, product]*self.tactical_model.y[cluster, product].value if (self.tactical_model.y[cluster, product].value)> 1e-6 else 0,
                'Profit': self.tactical_model.expected_profit[cluster, product]*self.tactical_model.y[cluster, product].value if (self.tactical_model.y[cluster, product].value)> 1e-6 else 0,
            }, index=[0])
            clus_prod_selected = pd.concat([clus_prod_selected, append_row], axis=0)

            self._logger.info(f'[ProductAllocation] The number of customers in cluster {cluster} that gets an offer of product {product} is {self.tactical_model.y[cluster, product].value}')
            total_expected_profit += self.tactical_model.expected_profit[cluster, product]*self.tactical_model.y[cluster, product].value
            total_expected_cost +=self.tactical_model.expected_cost[cluster, product]*self.tactical_model.y[cluster, product].value
        self.increased_budget = '${:,.2f}'.format(self.tactical_model.z.value)
        self._logger.info(f'[ProductAllocation] The increase correction in campaign budget is {self.increased_budget}')
        self.optimal_ROI = round(100*total_expected_profit/total_expected_cost,2)
        self.min_ROI = round(100*(1+self.tactical_model.hurdle_rate.value),2)

        money_expected_profit = '${:,.2f}'.format(total_expected_profit)
        money_expected_cost = '${:,.2f}'.format(total_expected_cost)
        self.money_budget = '${:,.2f}'.format(self.tactical_model.budget.value)

        print(f"\nFinancial reports.")
        print("___________________________________________________")
        print(f"Optimal total expected profit is {money_expected_profit}.")
        print(f"Optimal total expected cost is {money_expected_cost} with a budget of {self.money_budget} and an extra amount of {self.increased_budget}.")
        print(f"Optimal ROI is {self.optimal_ROI}% with a minimum ROI of  {self.min_ROI}%.")
        money_df = money_df.append({'money_expected_profit': round(total_expected_profit, 2), 
                                  'money_expected_cost': round(total_expected_cost, 2), 
                                  'money_budget': round(self.tactical_model.budget.value, 2),
                                  'increased_budget': round(self.tactical_model.z.value, 2),
                                  'optimal_ROI': self.optimal_ROI,
                                  'min_ROI': self.min_ROI}, ignore_index=True)
        return money_df, clus_prod_selected

    def __offer_allocation(self):
        self._logger.debug("[PostProcessing] Optimal assignment of product offers to customers is as such...")
        total_customer_profit = 0
        total_customer_cost = 0
        kvalue = None
        first = True
        num_assignments = 0
        clus_cust_prod_selected = pd.DataFrame()
        cust_money_df = pd.DataFrame()
        print("\nOptimal assignment of product offers to customers.")
        print("___________________________________________________")
        for cluster, customer, product in sorted(self.operational_model.ccp):
            append_row = pd.DataFrame({
                'cluster': cluster,
                'customer': customer,
                'product': product,
                'selected': 1 if self.operational_model.x[cluster, customer, product].value > 0.5 else 0,
                'cost': self.operational_model.customer_cost[cluster, customer, product] if self.operational_model.x[cluster, customer, product].value > 0.5 else 0,
                'profit': self.operational_model.customer_profit[cluster, customer, product] if self.operational_model.x[cluster, customer, product].value > 0.5 else 0,
            }, index=[0])
            clus_cust_prod_selected = pd.concat([clus_cust_prod_selected, append_row], axis=0)
            if cluster != kvalue:
                prevk = kvalue
                kvalue = cluster
                if not first:
                    print("___________________________________________________")
                    print(f"Number of assignments in cluster {prevk} is {num_assignments}")
                    print("___________________________________________________")
                    num_assignments = 0
                if first:
                    first = False
            if self.operational_model.x[cluster, customer, product].value > 0.5:
                profit = '${:,.2f}'.format(self.operational_model.customer_profit[cluster, customer, product])
                cost = '${:,.2f}'.format(self.operational_model.customer_cost[cluster, customer, product])
                print(f"Customer {customer} in cluster {cluster} gets an offer of product {product}:")
                print(f"The expected profit is {profit} at a cost of {cost}")
                total_customer_profit += self.operational_model.customer_profit[cluster, customer, product]*self.operational_model.x[cluster, customer, product].value
                total_customer_cost += self.operational_model.customer_cost[cluster, customer, product]*self.operational_model.x[cluster, customer, product].value
                num_assignments += 1
        print("___________________________________________________")
        print(f"Number of assignments in cluster {kvalue} is {num_assignments}")
        print("___________________________________________________\n")

        # Financial reports
        customers_ROI = round(100*total_customer_profit/total_customer_cost,2)
        money_customers_profit = '${:,.2f}'.format(total_customer_profit)
        money_customers_cost = '${:,.2f}'.format(total_customer_cost)

        print(f"\nFinancial reports.")
        print("___________________________________________________")
        print(f"Optimal total customers profit is {money_customers_profit}.")
        print(f"Optimal total customers cost is {money_customers_cost} with a budget of {self.money_budget} and an extra amount of {self.increased_budget}.")
        print(f"Optimal ROI is {customers_ROI}% with a minimum ROI of  {self.min_ROI}%.")
        cust_money_df = cust_money_df.append({'customer_expected_profit': round(total_customer_profit, 2), 
                                  'customer_expected_cost': round(total_customer_cost, 2), 
                                  'customer_optimal_ROI': customers_ROI}, ignore_index=True)
        return cust_money_df, clus_cust_prod_selected