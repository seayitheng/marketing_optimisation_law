from base import Logger


class Postprocessing(object):
     
    def __init__(self, model, money_budget=None, increased_budget=None, min_ROI=None):
        self._logger = Logger().logger
        self.model = model
        self._result_list = []
        self.prev_money_budget = money_budget
        self.prev_increased_budget = increased_budget
        self.prev_min_ROI = min_ROI
    
    def product_allocation(self):
        self._logger.debug("[PostProcessing] Optimal Products' allocation detail is as such...")
        total_expected_profit = 0
        total_expected_cost = 0
        for cluster, product in self.model.cp:
            if (self.model.y[cluster, product].value)> 1e-6:
                self._logger.info(f'[ProductAllocation] The number of customers in cluster {cluster} that gets an offer of product {product} is {self.model.y[cluster, product].value}')
                total_expected_profit += self.model.expected_profit[cluster, product]*self.model.y[cluster, product].value
                total_expected_cost +=self.model.expected_cost[cluster, product]*self.model.y[cluster, product].value
        increased_budget = '${:,.2f}'.format(self.model.z.value)
        self._logger.info(f'[ProductAllocation] The increase correction in campaign budget is {increased_budget}')
        optimal_ROI = round(100*total_expected_profit/total_expected_cost,2)
        min_ROI = round(100*(1+self.model.hurdle_rate.value),2)

        money_expected_profit = '${:,.2f}'.format(total_expected_profit)
        money_expected_cost = '${:,.2f}'.format(total_expected_cost)
        money_budget = '${:,.2f}'.format(self.model.budget.value)

        print(f"\nFinancial reports.")
        print("___________________________________________________")
        print(f"Optimal total expected profit is {money_expected_profit}.")
        print(f"Optimal total expected cost is {money_expected_cost} with a budget of {money_budget} and an extra amount of {increased_budget}.")
        print(f"Optimal ROI is {optimal_ROI}% with a minimum ROI of  {min_ROI}%.")

        return money_budget, increased_budget, min_ROI

    def offer_allocation(self):
        self._logger.debug("[PostProcessing] Optimal assignment of product offers to customers is as such...")
        total_customer_profit = 0
        total_customer_cost = 0
        kvalue = None
        first = True
        num_assignments = 0
        print("\nOptimal assignment of product offers to customers.")
        print("___________________________________________________")
        for cluster, customer, product in sorted(self.model.ccp):
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
            if self.model.x[cluster, customer, product].value > 0.5:
                profit = '${:,.2f}'.format(self.model.customer_profit[cluster, customer, product])
                cost = '${:,.2f}'.format(self.model.customer_cost[cluster, customer, product])
                print(f"Customer {customer} in cluster {cluster} gets an offer of product {product}:")
                print(f"The expected profit is {profit} at a cost of {cost}")
                total_customer_profit += self.model.customer_profit[cluster, customer, product]*self.model.x[cluster, customer, product].value
                total_customer_cost += self.model.customer_cost[cluster, customer, product]*self.model.x[cluster, customer, product].value
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
        print(f"Optimal total customers cost is {money_customers_cost} with a budget of {self.prev_money_budget} and an extra amount of {self.prev_increased_budget}.")
        print(f"Optimal ROI is {customers_ROI}% with a minimum ROI of  {self.prev_min_ROI}%.")