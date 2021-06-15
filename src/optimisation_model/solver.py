from base import Logger
from conf import Config
import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition


class ModelSolver(object):
    def __init__(self, model, solver_type=None): 
        self._logger = Logger().logger
        self.model = model
        self.results = None
        self.solver_type = solver_type or Config.OPTIMISATION_MODELLING_CONFIG['solver_type']
        self.__solve()

    def __solve(self)-> None:  
        """
        optimization model solver function. The solver function has
        transformations, which detects fixed variables and detects trival 
        constraints in oder to remove them.
        """
        pyo.TransformationFactory("contrib.detect_fixed_vars").apply_to(self.model)  # type: ignore
        pyo.TransformationFactory("contrib.deactivate_trivial_constraints").apply_to(self.model)  # type: ignore

        # initialise the solver object
        self._logger.debug("[ModelSolver] Solver object initiated...") 
        opt = pyo.SolverFactory(self.solver_type) # finding solver
        for k, v in Config.OPTIMISATION_MODELLING_CONFIG['solver_option'].get(self.solver_type).items():  # setting solver parameters, if any found in config
            opt.options[k] = v
        try:
            self._logger.debug("[ModelSolver] Solver starting...")
            results = opt.solve(self.model, tee=True)
            self.results = results
            self._logger.info("[ModelSolver] Solver completed.")
        except:
            opt = pyo.SolverFactory(self.solver_type, 
                                   executable=Config.OPTIMISATION_MODELLING_CONFIG['solver_loc'].get(self.solver_type)) # finding solver with path given, for local run
            for k, v in Config.OPTIMISATION_MODELLING_CONFIG['solver_option'].get(self.solver_type).items():  # setting solver parameters, if any found in config
                opt.options[k] = v
            try:
                results = opt.solve(self.model, tee=True)
                self.results = results
                self._logger.info("[ModelSolver] Solver completed.")
            except Exception as e:
                raise Exception(f"Model optimisation failed with {self.solver_type} with error message {e}.")
 

        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            self._logger.info("Solution is feasible and optimal")
            results.write()
        elif results.solver.termination_condition == TerminationCondition.infeasible:
            raise ValueError("Model optimisation resulted into an infeasible solution")

        self.model.optimised = True


if __name__ == "__main__":
    test = ModelSolver()
    print(test)
