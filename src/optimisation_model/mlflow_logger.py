import mlflow
import shutil
import inspect
import collections
from conf import Config
from pathlib import Path
from src.data_connectors import PandasFileConnector

mlflow.set_tracking_uri(Config.MLFLOW['TRACKING_URI'])  # Setting location to save models
mlflow.set_experiment(Config.MLFLOW['EXPERIMENT_NAME'])


class MLFlowLogger:

    @classmethod
    def log(cls, post_process_output):

        with mlflow.start_run():
            cls.__log_opt_solver(post_process_output)
            cls.__log_opt_model(post_process_output)
    
    @classmethod
    def __log_opt_solver(cls, post_process_output):

        artifact_folder = Config.MLFLOW['TEMP_ARTIFACT_DIR']
        Path(artifact_folder).mkdir(parents=True, exist_ok=True)

        # Solver Results [Tactical]
        post_process_output.operational_solver_results.results.write(
            filename=str(Path(artifact_folder, 'solver_results.json')), format='json'
        )
        results_dict = PandasFileConnector.load(Path(artifact_folder, 'solver_results.json'))
        for key, value in results_dict.items():
            results_dict[key] = value[0]
        results_dict = cls.flatten(results_dict)
        params_results_dict = {k: v for k, v in results_dict.items() if type(v) == str and v is not None}
        metrics_results_dict = {k: v for k, v in results_dict.items() if type(v) != str and v is not None}

        # add few model parameters
        tactical_expected_money = post_process_output.money_df.to_dict(orient='records')
        tactical_expected_money_dict = collections.ChainMap(*tactical_expected_money)
        for k, v in tactical_expected_money_dict.items():
            metrics_results_dict[k] = v

        operational_expected_money = post_process_output.cust_money_df.to_dict(orient='records')
        operational_expected_money_dict = collections.ChainMap(*operational_expected_money)
        for k, v in operational_expected_money_dict.items():
            metrics_results_dict[k] = v

        # Logging to mlflow
        mlflow.log_params(params_results_dict)
        mlflow.log_metrics(metrics_results_dict)

    @classmethod
    def __log_opt_model(cls, post_process_output):

        artifact_folder = Config.MLFLOW['TEMP_ARTIFACT_DIR']
        # Post Processed Results
        tactical_expected_money = post_process_output.money_df
        cluster_product_assignment_data = post_process_output.clus_prod_selected
        operational_expected_money = post_process_output.cust_money_df
        cluster_product_customer_assignment_data = post_process_output.clus_cust_prod_selected

        PandasFileConnector.save(tactical_expected_money, Path(artifact_folder, "tactical_expected_money.csv"))
        PandasFileConnector.save(cluster_product_assignment_data, 
                                Path(artifact_folder, "cluster_product_assignment_data.csv"))
        PandasFileConnector.save(operational_expected_money, Path(artifact_folder, "operational_expected_money.csv"))
        PandasFileConnector.save(cluster_product_customer_assignment_data, Path(artifact_folder, "cluster_product_customer_assignment_data.csv"))

        # Logging to mlflow
        mlflow.log_artifacts(artifact_folder, artifact_path='postprocessing')

        shutil.rmtree(artifact_folder)  # Deleting temp folder
    
    @classmethod
    def flatten(cls, d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k #https://www.programcreek.com/python/example/3372/collections.MutableMapping
            if isinstance(v, collections.MutableMapping):
                items.extend(cls.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


