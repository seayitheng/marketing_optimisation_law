import orjson
import typing
import traceback
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from base import Logger
from main import main
from conf import Config
from src.api.api_models import EXAMPLE_JSON, OptimiseModelInput

# ========== API Definition ==========
class ORJSONResponse(JSONResponse):
    """Custom JSONResponse class for returning NaN float values in JSON."""
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(content)

app = FastAPI(default_response_class=ORJSONResponse)
app.logger = Logger().logger

@app.get("/")
async def home(request: Request):
    user_ip = request.client.host
    request.app.logger.info(f"[{user_ip}] Default home '/' is called.")
    return "Welcome to PyOptimisation Framework! Please refer to '/docs/' path for Swagger API documentation."

# ============================== Optimisation ==============================
@app.post('/optimise/run/', tags=['optimise'])
async def api_optimize_model(
    request: Request,
    inputs: OptimiseModelInput = Body(
        ..., example=EXAMPLE_JSON["OptimiseModelInput"]
    )
):
    """POST request, which calles the optimisation main.py function based on config settings or
    user-defined settings and returns the post-processed data as a JSON object.
    """
    user_ip = request.client.host
    inputs = inputs.dict()
    request.app.logger.info(f"[{user_ip}] /optim/run/ is called.")

    # Compiling import and export settings
    import_settings = {
        "database": {
            "server": Config.PROJECT_ENVIRONMENT,
            "import_table": inputs['import_db_table'],
        },
        "csv": {
            "import_filepath": inputs['import_csv_filepath'],
            "import_table": inputs['import_csv_filename'],
        }
    }
    export_settings = {
        "database": {
            "server": Config.PROJECT_ENVIRONMENT,
            "export_table": inputs['export_db_table'],
        },
        "csv": {
            "export_filepath": inputs['export_csv_filepath'],
            "export_table": inputs['export_csv_filename'],
        },
        "api": {
        }
    }
    try:
        # Get optimised results convert to dataframe
        output = main(solver_type=inputs['solver_type'], import_from=inputs['import_from'],
                     import_settings=import_settings[inputs['import_from']],
                     export_to=inputs['export_to'], export_settings=export_settings[inputs['export_to']])
        # Format to json and return
        request.app.logger.info(f"[{user_ip}] /optimise_run complete.")
        if inputs['export_to'] != 'api':
            return f"/optimise_run complete."
        else:
            return JSONResponse(content=output)

    except Exception as err:
        request.app.logger.error('[FastApi] Error {}, {}'.format(err, traceback.format_exc()))
        return JSONResponse(status_code=500, content=err)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.api_main:app", host='localhost', port=3000, debug=False, reload=False)
