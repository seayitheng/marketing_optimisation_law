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
    # MLFLOW details
    # ================================================================================
    MLFLOW = dict(
        TRACKING_URI="./mlruns/",  # Location where mlflow artifacts will be stored, can also be AWS S3 or Azure Bucket
        EXPERIMENT_NAME= "Experiment-1",
        TEMP_ARTIFACT_DIR="./tmp/",  # Temporary directory for storing artifacts, will be automatically deleted.
    )

    # ================================================================================
    # Model Input & Output Settings
    # ===============================================================================
    MODEL_INPUTOUTPUT = dict(
        import_from="csv",
        import_settings={
            "csv": {
                "import_filepath": FILES["RAW_DATA"],
                "import_table": ['cluster_data', 'customer_data', 'product_data', 'product_cost', 'product_profit'],
            }
        },
        export_to="csv",
        export_settings={
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
