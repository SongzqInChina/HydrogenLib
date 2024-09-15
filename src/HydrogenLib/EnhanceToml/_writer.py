def encode(toml_info: dict):
    res = ""
    for table in toml_info.keys():
        res += f"[{table}]"
        for key, value in toml_info[table].items():
            res += f"\n{key} = {value}"
            res += "\n"
    return res
