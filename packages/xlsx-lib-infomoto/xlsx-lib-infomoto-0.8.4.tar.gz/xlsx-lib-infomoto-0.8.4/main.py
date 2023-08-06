import glob
import os
import random
from typing import List

from xlsx_lib.domain.motorcycle_model.XlsxMotorcycleModel import XlsxMotorcycleModel
from xlsx_lib.domain.motorcycle_model.MotorcycleModelWorkbook import MotorcycleModelWorkbook


def create_motorcycle_model(filename: str):
    motorcycle_model_workbook: MotorcycleModelWorkbook = MotorcycleModelWorkbook(
        file=filename,
        filename=filename,
    )

    motorcycle_model: XlsxMotorcycleModel = motorcycle_model_workbook.motorcycle_model

    pass


def create_all_models() -> List[XlsxMotorcycleModel]:
    filenames: List[str] = glob.glob("./xlsx_lib/files/*.xlsx", recursive=True)

    models: List[XlsxMotorcycleModel] = list()
    # TODO: Create directory name

    directory_name: str = f"./xlsx_lib/json/{random.randint(0, 999)}"

    try:
        os.mkdir(directory_name)
    except OSError as error:
        print(error)

    for filename in filenames:
        create_motorcycle_model(
            filename=filename,
        )

    return models


if __name__ == "__main__":
    pass
