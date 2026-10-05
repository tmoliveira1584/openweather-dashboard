"""View model: contrato do backend com o frontend (seção 6.3 da arquitetura).

Por enquanto só traz a escala; os modelos Pydantic do view model entram na fatia 3.
"""

from typing import Literal

Scale = Literal["c", "f"]
