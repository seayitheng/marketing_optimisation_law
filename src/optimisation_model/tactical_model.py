import pyomo.environ as pyo
from src.optimisation_model.preprocessing import Preprocessing
from base import Logger
from itertools import product


class TacticalOptimisationModel(object):
    """
    This class defines the optimisation model objectives
    and its associated costraints.
    """
    def __init__(self, processed_data: Preprocessing):
        self._logger = Logger().logger
        self.processed_data = processed_data
        self.model = pyo.ConcreteModel()
        self.model.optimised = False
        self.__build_model()
        
    def __build_model(self):
        self._logger.debug("[ModelBuilding] Defining model indicies and sets initiated...")
        self.model.products = pyo.Set(initialize=[p.product_type for p in self.processed_data.product_list])
        self.model.clusters = pyo.Set(initialize=[k.cluster for k in self.processed_data.cluster_list])
        self.model.cp = pyo.Set(initialize=list(product(self.model.clusters, self.model.products)))
        self.model.cp.pprint()
        self._logger.info("[ModelBuilding] Defining model indicies and sets completed successfully.")

        self._logger.debug("[ModelBuilding] Defining model parameters initiated...")
        self.model.number_customers = pyo.Param(self.model.clusters, initialize={k.cluster: k.customer_count for k in self.processed_data.cluster_list}, domain=pyo.Any)
        self.model.min_offers = pyo.Param(self.model.products, initialize={p.product_type: p.product_count for p in self.processed_data.product_list}, domain=pyo.Any)
        self.model.expected_profit = pyo.Param(self.model.cp, initialize={g: self.processed_data.product_profit[g] for g in self.model.cp}, domain=pyo.Any)
        self.model.expected_cost = pyo.Param(self.model.cp, initialize={g: self.processed_data.product_cost[g] for g in self.model.cp}, domain=pyo.Any)
        # fixed given value
        self.model.hurdle_rate = pyo.Param(initialize=0.2) # fixed given value
        self.model.budget = pyo.Param(initialize=200)
        self._logger.info("[ModelBuilding] Defining model parameters completed successfully.")

        # define decision variables
        self._logger.debug("[ModelBuilding] Defining model decision variables initiated...")
        # Allocation of product offers to customers in clusters.
        self.model.y = pyo.Var(self.model.cp, domain=pyo.PositiveReals) # more than 0
        self.model.z = pyo.Var(domain=pyo.NonNegativeReals)
        self._logger.info("[ModelBuilding] Defining model decision variables completed successfully.")

        # set obhective function
        self._logger.debug("[ModelBuilding] Defining model objective function initiated...")
        self.model.obj = pyo.Objective(rule=self.objective, sense=pyo.maximize)
        self._logger.info("[ModelBuilding] Defining model objective function completed successfully.")
        # set Constraints
        self.__add_constraints()
        
    def __add_constraints(self):
        self._logger.info("[ModelBuilding] Defining model constraint function initiated...")
        # max offer constraint
        self.model.max_offers = pyo.ConstraintList()
        self._max_offers()
        # budget constraint
        self.model.budget_constraint = pyo.ConstraintList()
        self._budget_constraint()
        # min offer constraint
        self.model.min_offers_constraint = pyo.ConstraintList()
        self._min_offers()
        # min ROI constraint
        self.model.min_ROI_constraint = pyo.ConstraintList()
        self._min_ROI()
        self._logger.info("[ModelBuilding] Defining model constraint function completed successfully.")        
    
    @staticmethod
    def objective(model):
        
        M = 10000
        return pyo.quicksum(model.y[g]*model.expected_profit[g] for g in model.cp) - M*model.z
            
    @property
    def optimisation_model(self):
        return self.model
    
    def _max_offers(self):
        """
        Maximum number of offers of products for each cluster. Number of customers in cluster 
        that are offered product less than or equal to Number of customers in cluster
        """
        for k in self.model.clusters:
            exp = pyo.quicksum(self.model.y[k, j] for j in self.model.products)
            self.model.max_offers.add(exp <= self.model.number_customers[k])

    def _budget_constraint(self):
        """The marketing campaign budget constraint enforces that the total cost of the campaign should be less than the budget campaign. 
        """
        self.model.budget_constraint.add(pyo.quicksum(self.model.y[g]*self.model.expected_cost[g] for g in self.model.cp) <= self.model.budget + self.model.z)

    def _min_offers(self):
        """Minimum number of offers of each product.
        """
        for j in self.model.products:
            exp = pyo.quicksum(self.model.y[k, j] for k in self.model.clusters)
            self.model.min_offers_constraint.add(exp >= self.model.min_offers[j])
    
    def _min_ROI(self):
        """The minimum ROI constraint ensures that the ratio of total profits over cost is at least one plus the corporate hurdle rate.
        """
        self.model.min_ROI_constraint.add(pyo.quicksum(self.model.y[g]*self.model.expected_profit[g] for g in self.model.cp) - (1+self.model.hurdle_rate)*pyo.quicksum(self.model.y[g]*self.model.expected_cost[g] for g in self.model.cp)>=0)