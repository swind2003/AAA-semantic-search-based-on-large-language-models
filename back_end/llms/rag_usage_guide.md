# RAG系统使用指南

## 1. 系统概述

本RAG（检索增强生成）系统允许用户创建自定义的智能问答角色，每个角色可以基于特定的知识库回答问题。系统支持多种文档格式，使用向量数据库进行高效检索，并利用大型语言模型生成回答。

## 2. 安装与配置

### 2.1 环境要求

- Python 3.10+
- CUDA支持的GPU（推荐用于加速嵌入和模型推理）
- 足够的存储空间用于向量数据库

### 2.2 依赖安装

```bash
# 克隆项目
git clone https://github.com/your-repo/rag-system.git
cd rag-system

# 安装依赖
pip install -r requirements.txt
```

### 2.3 配置文件

在开始使用前，需要配置以下内容：

1. 模型路径：在`api.py`和`haystack_utils.py`中设置正确的模型路径
2. OpenAI API密钥：使用生成功能时需要提供
3. 存储路径：系统会在项目根目录的上一级创建`roles_db`目录

## 3. 基本使用流程

### 3.1 启动服务

```bash
# 启动角色管理API服务
python role_api.py

# 启动基础语义搜索API（可选）
python api.py
```

两个服务默认都在8080端口运行，实际部署时需要调整。

### 3.2 创建角色

创建角色需要提供以下信息：

- `user_id`：用户标识
- `role_id`：角色标识
- `llm`：使用的大语言模型（如"gpt-3.5-turbo"）
- `prompt`：角色的提示词
- 知识文档：要上传的文档文件

示例请求：

```python
import requests

url = "http://localhost:8080/create_role"

files = [
    ('files', ('document.pdf', open('document.pdf', 'rb'), 'application/pdf'))
]

data = {
    'user_id': 'user123',
    'role_id': 'legal_expert',
    'llm': 'gpt-3.5-turbo',
    'prompt': '你是一名法律专家，请根据提供的法律文档回答问题。'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### 3.3 查询角色

使用创建好的角色进行问答：

```python
import requests
import json

url = "http://localhost:8080/query"

payload = json.dumps({
    'user_id': 'user123',
    'role_id': 'legal_expert',
    'llm': 'gpt-3.5-turbo',
    'prompt': '你是一名法律专家，请根据提供的法律文档回答问题。',
    'openai_api_key': 'your-openai-api-key',
    'question': '什么情况下构成轻伤害罪？'
})

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload)
print(response.json())
```

### 3.4 添加新文档

向现有角色添加新的知识文档：

```python
import requests

url = "http://localhost:8080/add_files"

files = [
    ('files', ('new_document.pdf', open('new_document.pdf', 'rb'), 'application/pdf'))
]

data = {
    'user_id': 'user123',
    'role_id': 'legal_expert',
    'llm': 'gpt-3.5-turbo',
    'prompt': '你是一名法律专家，请根据提供的法律文档回答问题。'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### 3.5 删除角色

删除不再需要的角色：

```python
import requests
import json

url = "http://localhost:8080/delete_role"

payload = json.dumps({
    'user_id': 'user123',
    'role_id': 'legal_expert'
})

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload)
print(response.json())
```

## 4. 高级功能

### 4.1 自定义提示词

提示词是决定角色行为和回答风格的关键。良好的提示词应包括：

- 角色定位：明确角色是谁，具备什么专业知识
- 回答风格：指定回答的语气、长度和格式
- 特殊指令：如需要引用文档出处、需要列举多个方案等

示例：
```
你是一名专业的法律顾问，拥有丰富的中国法律知识。
请基于提供的法律文档，用专业但易于理解的语言回答问题。
回答应简明扼要，控制在300字以内。
如果问题超出文档范围，请明确指出而不是猜测。
请在适当情况下引用相关法律条款。
```

### 4.2 支持的文档格式

系统支持多种文档格式，包括但不限于：
- PDF文档（.pdf）
- Word文档（.docx, .doc）
- 文本文件（.txt）
- Markdown文件（.md）

### 4.3 性能优化

- **文档分割**：适当调整`split_length`和`split_overlap`参数可以优化检索效果
- **检索数量**：调整`top_k`参数可以控制检索的文档片段数量
- **向量模型**：可以选择不同的嵌入模型来平衡性能和效果

## 5. 故障排除

### 5.1 常见问题

1. **创建角色失败**
   - 检查文档格式是否支持
   - 确认存储路径是否存在且有写入权限
   
2. **查询返回空结果**
   - 检查OpenAI API密钥是否正确
   - 确认问题是否与知识库内容相关
   
3. **服务启动失败**
   - 确认端口是否被占用
   - 检查模型路径配置是否正确

### 5.2 日志查看

系统会在控制台输出关键操作日志，包括：
- 角色创建和删除
- 查询处理
- 错误信息

## 6. 示例应用场景

### 6.1 法律咨询助手

```python
# 创建法律咨询角色
api_role = role.Role(
    "law_firm", 
    "legal_assistant", 
    "gpt-3.5-turbo", 
    "你是一名专业法律顾问，精通中国民商法。请根据提供的法律文件回答用户问题。"
)
```

### 6.2 医疗知识库

```python
# 创建医疗顾问角色
api_role = role.Role(
    "hospital", 
    "medical_advisor", 
    "gpt-3.5-turbo", 
    "你是一名经验丰富的医生，请根据最新医学知识回答患者问题，但不要给出确定的诊断意见。"
)
```

### 6.3 企业知识库

```python
# 创建企业内部知识库角色
api_role = role.Role(
    "company", 
    "policy_advisor", 
    "gpt-3.5-turbo", 
    "你是公司的内部政策顾问，熟悉所有公司规章制度。请简明扼要地回答员工关于公司政策的问题。"
)
``` 