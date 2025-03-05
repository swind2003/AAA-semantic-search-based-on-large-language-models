# RAG系统项目分析

## 1. 项目概述

这是一个基于检索增强生成（Retrieval-Augmented Generation, RAG）技术的智能问答系统，允许用户创建和管理自定义"角色"，每个角色都可以基于特定的文档集合和提示词（Prompt）来回答问题。系统利用向量数据库存储文档内容，通过语义搜索检索相关内容，并使用LLM（大型语言模型）生成回答。

## 2. 项目架构

### 2.1 核心组件

```
├── api.py                  # 基础API服务
├── role.py                 # 角色类实现
├── role_api.py             # 角色管理API
├── test/                   # 测试模块
└── utils/                  # 工具函数
    ├── haystack_utils.py   # Haystack框架工具
    ├── langchain_utils.py  # LangChain框架工具
    └── process_utils/      # 数据处理工具
```

### 2.2 工作流程

1. **角色创建**：用户创建角色，上传相关文档
2. **文档处理**：系统处理文档并创建向量数据库
3. **查询处理**：用户提问时，系统检索相关文档片段并利用LLM生成回答
4. **角色管理**：支持更新角色知识库、删除角色等操作

## 3. 关键功能详解

### 3.1 角色（Role）机制

角色是系统的核心概念，由以下属性组成：
- `user_id`：用户标识
- `role_id`：角色标识
- `llm`：使用的大语言模型
- `prompt`：角色的提示词
- `db_path`：角色知识库路径

每个角色有自己的知识库，可以独立回答问题，实现个性化的智能助手。

### 3.2 文档处理与向量化

系统使用Haystack或LangChain框架处理文档：
1. 文档分割：将长文档分割成适合检索的小段落
2. 向量化：使用嵌入模型（如m3e-base）将文本转换为向量
3. 存储：将向量存储在FAISS索引中，提供高效检索

```python
# 文档预处理示例
preprocessor = nodes.PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    split_by="word",
    split_length=100,
    split_overlap=50,
    split_respect_sentence_boundary=True,
)
```

### 3.3 检索与生成

查询处理的主要步骤：
1. 向量化查询：将用户问题转换为向量
2. 相似性检索：在FAISS索引中找到相关文档片段
3. 提示词构建：结合检索结果和角色提示词
4. 回答生成：调用LLM（如GPT-3.5）生成最终回答

```python
# 生成式QA管道示例
qa_prompt = """
请根据所给的文件如实回答问题。
Question:{query}
Documents:{join(documents)}
Answer:
"""
```

### 3.4 API接口

系统提供以下主要API接口：
- `/query`：使用角色回答问题
- `/create_role`：创建新角色并上传知识文档
- `/add_files`：向现有角色添加文档
- `/delete_role`：删除角色

## 4. 技术栈

- **Web框架**：FastAPI
- **向量数据库**：FAISS
- **文本处理**：Haystack、LangChain
- **嵌入模型**：m3e-base
- **语言模型**：ChatGLM2-6B（本地）、GPT-3.5（OpenAI API）

## 5. 优势与特点

- **多角色支持**：可创建多个专业领域的智能助手
- **知识隔离**：不同角色的知识库相互独立
- **灵活性**：支持多种语言模型，可本地部署或调用云服务
- **可扩展性**：可轻松添加新文档扩充知识库

## 6. 系统扩展方向

1. **多模态支持**：处理图像、音频等非文本数据
2. **角色交互**：实现角色之间的协作与对话
3. **知识更新**：自动从网络获取最新信息
4. **细粒度权限**：增强用户权限与隐私管理

## 7. 使用示例

```python
# 创建角色
api_role = role.Role("user123", "legal_expert", "gpt-3.5-turbo", "你是一名法律专家...")
api_role.determine_db_path()
api_role.create_role()

# 使用角色回答问题
answer = api_role.use_role(
    "openai_api_key",
    "因冲突将他人打伤，导致右额部粉碎性骨折、右眼眶骨骨折，请问应该如何判处？"
)
```

## 8. 总结

该RAG系统通过结合检索技术和生成式AI，实现了基于特定知识库的智能问答功能，特别适合构建垂直领域的专业助手。系统的角色机制提供了灵活性和可扩展性，使其能够适应各种应用场景，如法律咨询、医疗辅助、教育辅导等。 