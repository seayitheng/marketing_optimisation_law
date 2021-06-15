from conf import Config
from pydantic import BaseModel
from typing import List, Optional

# ================================================================================
# Example JSON Inputs to be displayed on Swagger docs UI
# ================================================================================
EXAMPLE_JSON = {
    'OptimiseModelInput': {
        "budget": 2000,
        "roi": 120,
        "cluster": [{
                        "Cluster": "k1",
                        "Count": 5
                    },{
                        "Cluster": "k2",
                        "Count": 5
                    }],
        "product": [{
                        "Product_Type": "p1", 
                        "Count": 2
                    }, {
                        "Product_Type": "p2", 
                        "Count": 2
                    }],
        "cost": [{
                    "Product_Type_Cost": "p1", 
                    "k1": 200, 
                    "k2": 300
                }, {
                    "Product_Type_Cost": "p2", 
                    "k1": 100, 
                    "k2": 200
                }],
        "profit": [{
                        "Product_Type_Profit": "p1", 
                        "k1": 2000, 
                        "k2": 3000
                    }, {
                        "Product_Type_Profit": "p2", 
                        "k1": 1000, 
                        "k2": 2000
                    }],
        "cust_cost_profit": [{
                                "Cluster": "k1", 
                                "Customer": "c1", 
                                "Product": "p1", 
                                "Cost": 205, 
                                "Profit": 2050
                            }, {
                                "Cluster": "k1", 
                                "Customer": "c2", 
                                "Product": "p1", 
                                "Cost": 195, 
                                "Profit": 1950
                            }, {
                                "Cluster": "k1", 
                                "Customer": "c3", 
                                "Product": "p1", 
                                "Cost": 200, 
                                "Profit": 2000
                            }, {
                                "Cluster": "k1", 
                                "Customer": "c4", 
                                "Product": "p1", 
                                "Cost": 210, 
                                "Profit": 2100
                            }, {
                                "Cluster": "k1", 
                                "Customer": "c5", 
                                "Product": "p1",
                                "Cost": 190, 
                                "Profit": 1900
                            }, {
                                "Cluster": "k2", 
                                "Customer": "c6", 
                                "Product": "p1", 
                                "Cost": 300, 
                                "Profit": 3000
                            }, {
                                "Cluster": "k2", 
                                "Customer": "c7", 
                                "Product": "p1", 
                                "Cost": 290, 
                                "Profit": 2900
                            }, {
                                "Cluster": "k2", 
                                "Customer": "c8", 
                                "Product": "p1", 
                                "Cost": 305, 
                                "Profit": 3050
                            }, {
                                "Cluster": "k2", 
                                "Customer": 
                                "c9", "Product": 
                                "p1", "Cost": 310, 
                                "Profit": 3100
                            }, {
                                "Cluster": "k2",
                                "Customer": "c10", 
                                "Product": "p1", 
                                "Cost": 295, 
                                "Profit": 2950
                            }, {
                                "Cluster": "k1", 
                                "Customer": "c1", 
                                "Product": "p2", 
                                "Cost": 105, 
                                "Profit": 1050
                            }, {
                                "Cluster": "k1", 
                                "Customer": "c2", 
                                "Product": "p2", 
                                "Cost": 95, 
                                "Profit": 950
                            }, {
                                "Cluster": "k1", 
                                "Customer": "c3", 
                                "Product": "p2", 
                                "Cost": 100, 
                                "Profit": 1000
                            }, {
                                "Cluster": "k1", 
                                "Customer": "c4", 
                                "Product": "p2", 
                                "Cost": 110, 
                                "Profit": 1100
                            }, {
                                "Cluster": "k1",
                                "Customer": "c5", 
                                "Product": "p2", 
                                "Cost": 90, 
                                "Profit": 900
                            }, {
                                "Cluster": "k2", 
                                "Customer": "c6", 
                                "Product": "p2", 
                                "Cost": 200, 
                                "Profit": 2000
                            }, {
                                "Cluster": "k2", 
                                "Customer": "c7",
                                "Product": "p2", 
                                "Cost": 190, 
                                "Profit": 1900
                            }, {
                                "Cluster": "k2", 
                                "Customer": "c8", 
                                "Product": "p2", 
                                "Cost": 205, 
                                "Profit": 2050
                            }, {
                                "Cluster": "k2", 
                                "Customer": "c9", 
                                "Product": "p2", 
                                "Cost": 210, 
                                "Profit": 2100
                            }, {
                                "Cluster": "k2", 
                                "Customer": "c10", 
                                "Product": "p2", 
                                "Cost": 195, 
                                "Profit": 1950
                            }]
    },
}

# ================================================================================
# OPTIMISATION MODEL INPUTS
# ================================================================================
class OptimiseModelInput(BaseModel):
    """Optimisation model input"""
    budget: Optional[int]
    roi: Optional[int]
    cluster: List[dict]
    product: List[dict]
    cost: List[dict]
    profit: List[dict]
    cust_cost_profit: List[dict]