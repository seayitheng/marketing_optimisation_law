import orjson
import typing
import traceback
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from conf import Logger
from main import main
from conf import Config
from src.api.api_pydantic_models import * # pydantic Models for Swagger API Docs
import pandas as pd
import collections


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
    return "Welcome to LAW Marketing Optimisation Use Case! Please refer to '/docs/' path for Swagger API documentation."

# ============================== Optimisation ==============================
@app.post('/run_optimisation/', tags=['optimisation'])
async def run_optimisation(
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
    request.app.logger.info(f"[{user_ip}] /run_optimisation/ is called.")
    assert inputs is not None, "`data` was not provided for model run"

    # Run optimisation
    optimisation_results = main(inputs)
    request.app.logger.info(f"[{user_ip}] /run_optimisation complete.")
    return JSONResponse(content=optimisation_results.compiled_json_results)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.api_main:app", host='localhost', port=3000, debug=False, reload=False)
