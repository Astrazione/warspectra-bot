from attr import dataclass
from app.models.updating_data_args import UpdatingDataArgs


@dataclass
class RequestValidationResult:
    """
    Результат валидации запроса на обновление данных.
    """
    status: bool
    data_args: UpdatingDataArgs
    