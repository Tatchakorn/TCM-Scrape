import json
from pathlib import Path


class JsonHandler:
    '''As the name suggests'''
    
    def __init__(self, file: Path) -> None:
        self.json_file = file

    
    def read(self) -> dict:
        if not self.json_file.exists():
            self.write({})
        with open(self.json_file, 'r', encoding='utf-8') as f:
            j = dict(json.loads(f.read()))
        return j
    
    
    def write(self, data: dict):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, indent=4, sort_keys=True, fp=f, ensure_ascii=False)

    
    def update(self, key: str, val: any) -> None:
        '''Shallow update'''
        data = self.read()
        data[key] = val
        self.write(data)