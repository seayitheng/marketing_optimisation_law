from conf import Config
from pydantic import BaseModel
from typing import Optional

# ================================================================================
# Example JSON Inputs to be displayed on Swagger docs UI
# ================================================================================
EXAMPLE_JSON = {
    'OptimiseModelInput': {
        "solver_type": Config.OPTIMISATION_MODELLING_CONFIG['solver_type'],
        "import_from": Config.MODEL_INPUTOUTPUT['import_from'],
        "import_db_table": Config.MODEL_INPUTOUTPUT['import_settings']['database']['import_table'],
        "import_csv_filepath": Config.MODEL_INPUTOUTPUT['import_settings']['csv']['import_filepath'],
        "import_csv_filename": Config.MODEL_INPUTOUTPUT['import_settings']['csv']['import_table'],
        "export_to": 'api',
        "export_db_table": Config.MODEL_INPUTOUTPUT['export_settings']['database']['export_table'],
        "export_csv_filepath": Config.MODEL_INPUTOUTPUT['export_settings']['csv']['export_filepath'],
        "export_csv_filename": Config.MODEL_INPUTOUTPUT['export_settings']['csv']['export_table'],
    },
}

# ================================================================================
# OPTIMISATION MODEL INPUTS
# ================================================================================
class OptimiseModelInput(BaseModel):
    """Optimisation model settings"""
    solver_type: Optional[str] = Config.OPTIMISATION_MODELLING_CONFIG['solver_type']
    import_from: Optional[str] = Config.MODEL_INPUTOUTPUT['import_from']
    import_db_table: Optional[list] = Config.MODEL_INPUTOUTPUT['import_settings']['database']['import_table']
    import_csv_filepath: Optional[str] = Config.MODEL_INPUTOUTPUT['import_settings']['csv']['import_filepath']
    import_csv_filename: Optional[list] = Config.MODEL_INPUTOUTPUT['import_settings']['csv']['import_table']
    export_to: Optional[str] = 'api'
    export_db_table: Optional[list] = Config.MODEL_INPUTOUTPUT['export_settings']['database']['export_table']
    export_csv_filepath: Optional[str] = Config.MODEL_INPUTOUTPUT['export_settings']['csv']['export_filepath']
    export_csv_filename: Optional[list] = Config.MODEL_INPUTOUTPUT['export_settings']['csv']['export_table']
