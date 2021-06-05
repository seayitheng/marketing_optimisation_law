import os
import pytest
import numpy as np
import pandas as pd
from main import *
from conf import Config
from base import DatabaseConnector, PandasFileConnector, YAMLFileConnector

@pytest.fixture
def connect_db():
    db_connection = YAMLFileConnector.load('conf/local/db_connection.yml')[Config.PROJECT_ENVIRONMENT]
    db_connector = DatabaseConnector(**db_connection)
    return db_connector

@pytest.fixture
def expected_utilisation_hour():
    expected_utilisationHour = {
        'Albert': 187.0,
        'Bob': 194.0,
        'Carlos': 156.0,
        'Doris': 230.0,
        'Ed': 0.0,
        'Flor': 184.0,
        'Gina': 0.0,
        'Total': 951.0
        }
    return expected_utilisationHour

@pytest.mark.order(1)
def test_opt_modelrun_csv():
    """Check if opt model has been carried out successfully with 3 csv files 
    generated at data\07_model_output.""" 
    dir = 'data/07_model_output'
    beforeFiles = 0
    afterFiles = 0
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))  # clear files in the folder
    for _, _, files in os.walk(dir):
        for file_exit in files:
            beforeFiles += 1  # count files in the folder before model run
    main(solver_type='cbc', export_to='csv')
    for _, _, files in os.walk(dir):
        for file_exit in files:
            afterFiles += 1  # count files in the folder after model run
    assert afterFiles > beforeFiles, "No new files detected in ./data/07_model_output folder."

@pytest.mark.order(2)
def test_db_connection(connect_db):
    """Push output csv files to db and check the data."""
    dir = 'data/07_model_output'
    for _, _, files in os.walk(dir):
        for file_exit in files:
            data = PandasFileConnector.load(os.path.join(dir, file_exit))
            data = data.drop(data.filter(regex='Unnamed:').columns, axis=1)
            connect_db.save(data, file_exit.split('.')[0]+"_unittest")
    assignment_data = PandasFileConnector.load(os.path.join(dir, 'assignment_output_cbc.csv'))  # load random one file
    assignment_data = assignment_data[[x for x in assignment_data.columns if x != 'Unnamed: 0']]
    assignment_df = connect_db.load('assignment_output_cbc_unittest')
    assignment_df = assignment_df[assignment_data.columns]
    assert assignment_data.equals(assignment_df), "Database do not \
    have such table, please check."  # Both tables should match

@pytest.mark.order(3)
def test_utilization_hour_cbc(connect_db, expected_utilisation_hour):
    """Check if individual and total utilization hour is the same as expected utilization hour."""
    expected_hour = pd.DataFrame(expected_utilisation_hour, index=[0]).T.reset_index()
    expected_hour.columns = ['Technician', 'Used_Hour']
    assignment_df = connect_db.load('utilization_output_cbc_unittest')
    assignment_df_sub = assignment_df[['Technician', 'Used_Hour']]
    assert expected_hour.equals(assignment_df_sub), "2 tables are not identical, \
    assignment hour is not as expected. Please check."  # Both tables should match

#########################################################################################################
###################### Optimisation Model Constraint Unit Test Example ##################################
# unit test for optimisation constraints, not the exhaustive list
@pytest.mark.order(4)
def test_technician_capacity(connect_db):
    """"Check if individual technician used hour is more than the total capacity hour."""
    utilization_df = connect_db.load('utilization_output_cbc_unittest')
    utilization_df['flag'] = np.where(utilization_df['Used_Hour'] > utilization_df['Total_Hour'], 1, 0) 
    assert len(utilization_df[utilization_df['flag'] == 1]) == 0, f"Technician capacity constraint is \
    violated for technician {utilization_df['Technician'][utilization_df['flag']==1].to_list()}. Please check"

@pytest.mark.order(5)
def test_one_technician_constraint(connect_db):
    """Check if each customer has only been to 1 unique technician."""
    assignment_df = connect_db.load('assignment_output_cbc_unittest')
    grp_by = assignment_df.groupby('Customer')['Technician'].nunique().reset_index()
    grp_by['flag'] = np.where(grp_by['Technician'] > 1, 1, 0) 
    assert len(grp_by[grp_by['flag'] == 1]) == 0, f"Technician assignment constraint \
    is violated for customer {grp_by['Customer'][grp_by['flag']==1].to_list()}. Please check"

@pytest.mark.order(6)
def test_same_depot_constraint(connect_db):
    """Check if each technician start location is their start depot."""
    technicians_input = connect_db.load('technicians_input')
    technicians_input = technicians_input.iloc[2:]
    technicians_input = technicians_input[['Unnamed: 0', 'Depot']]
    routing_df = connect_db.load('routing_output_cbc_unittest')
    routing_df = routing_df[routing_df['Start_Time'].notnull()]
    grp_by_min = routing_df.groupby('Technician')['Start_Time'].min().reset_index()
    merge_min = pd.merge(routing_df, grp_by_min, on=['Technician'], how='left')
    merge_min['flag'] = np.where(merge_min['Start_Time_x'] == merge_min['Start_Time_y'], 1, 0)
    merge_min = merge_min[merge_min['flag'] == 1]
    merge_df = pd.merge(merge_min, technicians_input, left_on=['Technician'], 
                       right_on=['Unnamed: 0'], how='left')
    merge_df['flag'] = np.where(merge_df['Start_Loc'] == merge_df['Depot'], 0, 1)
    assert len(merge_df[merge_df['flag'] == 1]) == 0, f"Technician start location is \
    different from depot for technician {merge_df['Technician'][merge_df['flag'] == 1]}. Please check. "

@pytest.mark.order(7)
def test_delete_unittest_outputDB(connect_db):
    """Delete tables in db, after that, when load table, df should be null"""
    connect_db.execute_statement('DROP TABLE routing_output_cbc_unittest', expect_output=False)
    connect_db.execute_statement('DROP TABLE assignment_output_cbc_unittest', expect_output=False)
    connect_db.execute_statement('DROP TABLE utilization_output_cbc_unittest', expect_output=False)
    assignment_df = connect_db.load('assignment_output_cbc_unittest')  # load random one file
    assert assignment_df is None, "tables are not deleted successfully in DB"