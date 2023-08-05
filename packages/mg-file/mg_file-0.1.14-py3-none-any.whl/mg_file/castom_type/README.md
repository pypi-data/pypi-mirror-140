```python
from mg_file.castom_type import DefTypeDict


class Settings(DefTypeDict):
    port: int = 7070
    host: str = "0.0.0.0"


Settings(port=8080)
# {"port":8080, host="0.0.0.0"}
```

