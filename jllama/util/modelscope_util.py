import requests
import re


def get_modelscope_model_file(repo: str, revision="master", root="", gguf_only: bool = True,
                              allow_file_pattern: str = "*"):
    if allow_file_pattern == "*":
        allow_file_pattern = ".*"
    resp = requests.get(
        "https://modelscope.cn/api/v1/models/" + repo + "/repo/files?Revision=" + revision + "&Root=" + root)
    if resp.status_code == 200:
        data = resp.json()
        files = data["Data"]["Files"]
        file_list = []
        sub_list = []
        for item in files:
            if item["Type"] == "tree":
                sub_list += get_modelscope_model_file(repo, revision, item["Name"], gguf_only, allow_file_pattern)
                continue

            if re.search(allow_file_pattern, item["Name"]):
                if gguf_only:
                    if item["Name"].endswith(".gguf"):
                        file_list.append(item)
                else:
                    file_list.append(item)

        if len(sub_list) > 0:
            file_list += sub_list
        return file_list
    else:
        print(f"resp http status= {resp.status_code}")
    return None


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
        # print(json.dumps(res))
        if res.get("Code") == 200:
            data = res.get("Data")
            model = data.get("Model")
            total = model.get("TotalCount")
            result["total"] = total
            models = model.get("Models")
            model_list = []
            for item in models:
                model_name = item.get("Name")
                create_by = item.get("CreatedBy")
                org_name = item.get("Organization").get("Name")
                if org_name:
                    model_list.append(f"{org_name}/{model_name}")
                else:
                    model_list.append(f"{create_by}/{model_name}")
            result["models"] = model_list
    else:
        result["success"] = False
        result["error"] = f"http status= {response.status_code}, error={response.text}"
    return result


if __name__ == '__main__':
    print(search_modelscope_model("Qwen3-0.6B-GGUF"))
    import json

    print(json.dumps(
        get_modelscope_model_file("deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", gguf_only=False, allow_file_pattern="*")))
