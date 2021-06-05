from pathlib import Path

class Config(object):

    # ================================================================================
    # Project details & folders
    # ================================================================================
    NAME = dict(
        full="LAW 2021 Marketing Optimisation",
        short="Marketing_Optim",
    )

    PROJECT_ENVIRONMENT = "development"

    # File structure
    FILES = dict(
        RAW_DATA=Path('data', '01_raw'),
        INTERMEDIATE_DATA=Path('data', '02_intermediate'),
        PRIMARY_DATA=Path('data', '03_primary'),
        FEATURE_DATA=Path('data', '04_feature'),
        MODEL_INPUT_DATA=Path('data', '05_model_input'),
        MODELS_DATA=Path('data', '06_models'),
        MODEL_OUTPUT=Path('data', '07_model_output'),
        REPORTING=Path('data', '08_reporting'),
    )

    for file, file_path in FILES.items():
        Path(file_path).mkdir(parents=True, exist_ok=True)  

    # ================================================================================
    # Model Input & Output Settings
    # ===============================================================================
    MODEL_INPUTOUTPUT = dict(
        import_from="database",
        import_settings={
            "database": {
                "server": PROJECT_ENVIRONMENT,
                "import_table": ['technicians_input', 'locations_input', 'customers_input'],
            },
            "csv": {
                "import_filepath": FILES["RAW_DATA"],
                "import_table": ['technicians_input', 'locations_input', 'customers_input'],
            }
        },
        export_to="database",
        export_settings={
            "database": {
                "server": PROJECT_ENVIRONMENT,
                "export_table": ['assignment_output', 'routing_output', 'utilization_output'],
            },
            "csv": {
                "export_filepath": FILES["MODEL_OUTPUT"],
                "export_table": ['assignment_output', 'routing_output', 'utilization_output'],
            },
        }
    )

    # ================================================================================
    # Optimisation Model Configurations by Solver Types
    # ================================================================================
    OPTIMISATION_MODELLING_CONFIG = dict(
        solver_type='cbc', # or cbc
        solver_loc={
            'cbc':'src\optimisation_model\cbc'
        },
        solver_option=dict(
            cbc={
                'ratioGap': 0.01,
                'nodeStrategy': 'hybrid',
                'seconds': 600,
                'randomCbcSeed': 999,
            },
            glpk={
                'tmlim': 600,
                'mipgap': 0.02,
                'seed': 999,
            }
        ),
    )
