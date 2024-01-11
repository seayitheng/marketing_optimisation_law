
from src.optimisation_model.preprocessing import Preprocessing
from src.optimisation_model.tactical_model import TacticalOptimisationModel
from src.optimisation_model.operation_model import OperationalOptimisationModel
from src.optimisation_model.solver import ModelSolver
from src.optimisation_model.postprocessing import Postprocessing
from src.optimisation_model.mlflow_logger import MLFlowLogger
from conf import Logger
_logger = Logger().logger

# main function
def main(input=None):
    """
    This function represents the main entry-point function,
    which does the processing, creates the optimsiation model,
    and does the post-processing.
    """
    # process the data using Preprocessing class
    _logger.debug("[MainPreprocessing] initiated...")
    processData = Preprocessing(input)
    _logger.debug("[MainPreprocessing] completed successfully.")

    # build the optimisation model, where objectives and constraints are defined.
    _logger.debug("[TacticalOptModel] initiated...")

    tactical_model = TacticalOptimisationModel(processData)
    # get the created model
    tactical_opt_model = tactical_model.model
    #solver the optimisation model
    tactical_model_solver = ModelSolver(tactical_opt_model)
    _logger.debug("[TacticalOptModel] completed successfully.")

    _logger.debug("[OperationalOptModel] initiated...")
    operation_model = OperationalOptimisationModel(tactical_opt_model, processData)
    operation_opt_model = operation_model.model

    operational_model_solver = ModelSolver(operation_opt_model)
    
    _logger.debug("[OperationalOptModel] completed successfully.")
    
    _logger.debug("[PostProcessing] OperationalOptModel initiated...")
    post_process_output = Postprocessing(tactical_model_solver, operational_model_solver, tactical_opt_model, operation_opt_model, export=True)
    _logger.debug("[PostProcessing] OperationalOptModel completed successfully.")

    _logger.debug("[MLFlow Logging] initiated...")
    MLFlowLogger.log(post_process_output)
    _logger.debug("[MLFlow Logging] completed successfully.")

    return post_process_output

if __name__ == "__main__":
    main()
    
    
