import requests


def build_req(model_name: str, page_size: int, text_generation_only: bool = True, gguf_only: bool = True) -> dict:
    req = {
        "PageSize": page_size,
        "PageNumber": 1,
        "SortBy": "Default",
        "Target": "",
        "SingleCriterion": [],
        "Name": model_name
    }
    if text_generation_only:
        req["Criterion"] = [
            {
                "category": "tasks",
                "predicate": "contains",
                "values": [
                    "text-generation"
                ],
                "sub_values": []
            }
        ]
    if gguf_only:
        req["Criterion"].append({
            "category": "libraries",
            "predicate": "contains",
            "values": [
                "gguf"
            ]
        })
    return req


def search_modelscope_model(model_name, page_size=50, text_generation_only: bool = True,
                            gguf_only: bool = True) -> dict:
    url = "https://modelscope.cn/api/v1/dolphin/models"
    req = build_req(model_name, page_size, text_generation_only, gguf_only)

    response = requests.put(url, json=req)
    result = {}
    # 检查响应状态码
    if response.status_code == 200:
        result["success"] = True
        # 请求成功，处理响应数据
        res = response.json()
        if res.get("Code") == 200:
            data = res.get("Data")
            model = data.get("Model")
            total = model.get("TotalCount")
            result["total"] = total
            models = model.get("Models")
            model_list = []
            for item in models:
                model_list.append(item.get("Name"))
            result["models"] = model_list
    else:
        result["success"] = False
        result["error"] = f"http status= {response.status_code}, error={response.text}"
    return result

if __name__ == '__main__':
    print(search_modelscope_model("llama"))