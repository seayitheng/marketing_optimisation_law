import pyomo.environ as pyo
from base import Logger
from itertools import product
from src.optimisation_model.preprocessing import Preprocessing


class OperationalOptimisationModel(object):
    """
    This class defines the optimisation model objectives
    and its associated costraints.
    """
    def __init__(self, tactical_model, processed_data:Preprocessing):
        self._logger = Logger().logger
        self.tactical_model = tactical_model
        self.processed_data = processed_data
        self.model = pyo.ConcreteModel()
        self.model.optimised = False
        self.__build_model()
        
    def __build_model(self):
        self._logger.debug("[ModelBuilding] Defining model indicies and sets initiated...")
        self.model.customers = pyo.Set(initialize=[c.name for c in self.processed_data.customer_list])
        self.model.products = pyo.Set(initialize=[p.product_type for p in self.processed_data.product_list])
        self.model.clusters = pyo.Set(initialize=[k.cluster for k in self.processed_data.cluster_list])
        self.model.ccp = pyo.Set(initialize=[c.customer_cluster_list for c in self.processed_data.customer_list])        

        self._logger.info("[ModelBuilding] Defining model indicies and sets completed successfully.")

        self._logger.debug("[ModelBuilding] Defining model parameters initiated...")
        self.model.customer_profit = pyo.Param(self.model.ccp, initialize={cp: self.processed_data.customer_profit[cp] for cp in self.model.ccp}, domain=pyo.Any)
        self.model.customer_cost = pyo.Param(self.model.ccp, initialize={cp: self.processed_data.customer_cost[cp] for cp in self.model.ccp}, domain=pyo.Any)
        self._logger.info("[ModelBuilding] Defining model parameters completed successfully.")

        # define decision variables
        self._logger.debug("[ModelBuilding] Defining model decision variables initiated...")
        # Allocation of product offers to customers in clusters.
        self.model.x = pyo.Var(self.model.ccp, domain=pyo.Binary)
        self._logger.info("[ModelBuilding] Defining model decision variables completed successfully.")

        # set obhective function
        self._logger.debug("[ModelBuilding] Defining model objective function initiated...")
        self.model.obj = pyo.Objective(rule=self.objective, sense=pyo.maximize)
        self._logger.info("[ModelBuilding] Defining model objective function completed successfully.")
        # set Constraints
        self.__add_constraints()
        
    def __add_constraints(self):
        self._logger.info("[ModelBuilding] Defining model constraint function initiated...")
        # product offer constraint
        self.model.product_offer = pyo.ConstraintList()
        self._product_offer()
        # offer limit constraint
        self.model.offer_limit = pyo.ConstraintList()
        self._offer_limit()
        self._logger.info("[ModelBuilding] Defining model constraint function completed successfully.")        
    
    @staticmethod
    def objective(model):
        return pyo.quicksum(model.x[cp]*model.customer_profit[cp] for cp in model.ccp)
            
    @property
    def optimisation_model(self):
        return self.model
    
    def _product_offer(self): # double is private, single for show. 
        """
        Allocate offers of a product to customers of each cluster.

        """
        for k in self.model.clusters:
            for j in self.model.products:
                exp = pyo.quicksum(self.model.x[cluster, customer, product] for cluster, customer, product in self.model.ccp if (cluster==k and product==j))
                self.model.product_offer.add(exp == self.tactical_model.y[k, j].value)

    def _offer_limit(self):
        """
        At most one product may be offered to a customer of a cluster.
        """
        ki = [('k1', 'c1'), 
              ('k1', 'c2'), 
              ('k1', 'c3'),
              ('k1', 'c4'), 
              ('k1', 'c5'), 
              ('k2', 'c6'), 
              ('k2', 'c7'), 
              ('k2', 'c8'), 
              ('k2', 'c9'), 
              ('k2', 'c10')]
        for k, i in ki:
            exp = pyo.quicksum(self.model.x[cluster, customer, product] for cluster, customer, product in self.model.ccp if (cluster==k and customer==i))
            self.model.offer_limit.add(exp<= 1)