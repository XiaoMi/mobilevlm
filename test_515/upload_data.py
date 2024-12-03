#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.

from huggingface_hub import HfApi, HfFolder

# 获取 API token
api = HfApi()
api.login(token="hf_***")

# 上传文件
api.upload_file(
    path_or_fileobj="./test_data.7z.001",  # 本地文件路径或文件对象
    path_in_repo="test_data.7z.001",  # 上传到仓库的路径
    repo_id="xwk123/mobilevlm_test",  # Hugging Face 仓库ID
    repo_type="dataset"  # 仓库类型
)

# 继续上传其他分卷压缩文件
api.upload_file(
    path_or_fileobj="./test_data.7z.002",
    path_in_repo="test_data.7z.002",
    repo_id="xwk123/mobilevlm_test",
    repo_type="dataset"
)
