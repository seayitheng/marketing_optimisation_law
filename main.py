
from src.optimisation_model.preprocessing import Preprocessing
from src.optimisation_model.tactical_model import TacticalOptimisationModel
from src.optimisation_model.operation_model import OperationalOptimisationModel
from src.optimisation_model.solver import ModelSolver
from src.optimisation_model.postprocessing import Postprocessing
from base import Logger
import pandas as pd
_logger = Logger().logger


def main():
    """
    This function represents the main entry-point function,
    which does the processing, creates the optimsiation model,
    and does the post-processing.
    """
    # process the data using Preprocessing class
    _logger.debug("[MainPreprocessing] initiated...")
    processData = Preprocessing()
    _logger.debug("[MainPreprocessing] completed successfully.")

    # build the optimisation model, where objectives and constraints are defined.
    _logger.debug("[TacticalOptModel] initiated...")

    tactical_model = TacticalOptimisationModel(processData)
    # get the created model
    tactical_opt_model = tactical_model.model
    #solver the optimisation model
    ModelSolver(tactical_opt_model)
    _logger.debug("[TacticalOptModel] completed successfully.")

    # post-processing of the solved model
    _logger.debug("[PostProcessing] TacticalOptModel initiated...")
    tactmodel = Postprocessing(tactical_opt_model)
    money_budget, increased_budget, min_ROI = tactmodel.product_allocation()
    #output = postprocessData.optim_result()
    _logger.debug("[PostProcessing] TacticalOptModel completed successfully.")

    _logger.debug("[OperationalOptModel] initiated...")
    operation_model = OperationalOptimisationModel(tactical_opt_model, processData)
    operation_opt_model = operation_model.model
    ModelSolver(operation_opt_model)
    _logger.debug("[OperationalOptModel] completed successfully.")
    _logger.debug("[PostProcessing] OperationalOptModel initiated...")
    optmodel = Postprocessing(operation_opt_model, money_budget, increased_budget, min_ROI)
    optmodel.offer_allocation()
    _logger.debug("[PostProcessing] OperationalOptModel completed successfully.")


if __name__ == "__main__":
    main()
    
    