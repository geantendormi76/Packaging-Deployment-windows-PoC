本项目完整记录了如何将一个基于 Python 的 RAG 服务在 Windows 环境下打包成独立可执行文件的全过程。

## 1. 环境准备 (Prerequisites)

在开始之前，请确保你的 Windows 系统已安装以下软件和工具：

* **Python 3.11+ for Windows**: 确保在安装时勾选 "Add Python to PATH" 选项。
* **Git for Windows**: 用于版本控制和克隆仓库。
* **Microsoft C++ Build Tools**: `llama-cpp-python` 编译时必需。
    * 通过 **Visual Studio Installer** 安装：在“工作负载”中选择 **“使用 C++ 的桌面开发”**。
* **(可选) NVIDIA GPU 和 CUDA 工具包**: 如果你打算使用 GPU 加速，则需要此项。本次 PoC 主要面向 CPU 运行 (在 `.env` 中设置了 `EMBEDDING_N_GPU_LAYERS=0`)。

## 2. 安装与配置 (Setup)

1.  **克隆或下载本项目仓库:**
    ```bash
    git clone <你的仓库URL>
    cd zhz_agent 
    ```

2.  **创建并激活 Python 虚拟环境:**
    ```powershell
    # 创建名为 .venv 的虚拟环境
    python -m venv .venv
    # 激活虚拟环境
    .\.venv\Scripts\activate
    ```

3.  **安装项目依赖:**
    ```powershell
    pip install -r requirements.txt
    ```
    * **`llama-cpp-python` 安装问题排查:** 如果此库安装失败，请确保已正确安装 C++ Build Tools。如果因 GPU 相关问题导致失败，你可以设置以下环境变量强制使用 CPU 模式进行编译：
        ```powershell
        $env:CMAKE_ARGS = "-DLLAMA_CUBLAS=OFF -DLLAMA_OPENBLAS=OFF" 
        pip install --no-cache-dir llama-cpp-python
        ```

4.  **准备模型文件:**
    * 在项目根目录 (`zhz_agent`) 下创建一个名为 `mini_service_payload` 的文件夹。
    * 从 Hugging Face 下载 Reranker 模型 (`Qwen/Qwen3-Reranker-0.6B-seq-cls`)，并将其**整个文件夹**放入 `mini_service_payload` 中。
    * 从 Hugging Face 下载 Embedding GGUF 模型 (`Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf`)，并将其 `.gguf` 文件放入 `mini_service_payload` 中。

5.  **配置环境变量 (`.env` 文件):**
    * 在项目根目录 (`zhz_agent`) 下创建一个名为 `.env` 的文件。
    * 添加以下内容。请注意，这里的路径用于**本地开发模式**，打包后的程序会自动寻找 `mini_service_payload` 文件夹。
        ```env
        # 请将这里的路径修改为你本地存放模型的绝对路径
        RERANKER_MODEL_PATH=C:\\path\\to\\your\\zhz_agent\\mini_service_payload\\Qwen3-Reranker-0.6B-seq-cls
        EMBEDDING_MODEL_PATH=C:\\path\\to\\your\\zhz_agent\\mini_service_payload\\Qwen3-Embedding-0.6B-Q8_0.gguf
        EMBEDDING_N_CTX=2048
        EMBEDDING_N_GPU_LAYERS=0
        ```
        *(提示: 在 Windows 的 `.env` 文件中，路径分隔符需要使用双反斜杠 `\\` 或正斜杠 `/`)*

## 3. 运行服务 (开发模式)

1.  确保你的 Python 虚拟环境已激活。
2.  运行主服务脚本:
    ```powershell
    python mini_rag_service_for_packaging.py
    ```
3.  服务启动后，默认监听 `http://localhost:8008`。你可以通过浏览器或 API 工具测试以下接口：
    * `http://localhost:8008/`
    * `http://localhost:8008/duckdb_test`
    * `http://localhost:8008/reranker_test`
    * `http://localhost:8008/embedding_test`

## 4. 使用 PyInstaller 打包

1.  确保你的 Python 虚拟环境已激活。
2.  确认项目根目录下存在 `mini_rag_app.spec` 文件，并已正确配置（尤其是在开发过程中反复调试过的 `datas` 和 `hiddenimports` 部分）。
3.  使用 `.spec` 文件运行 PyInstaller 进行打包:
    ```powershell
    pyinstaller --noconfirm --clean mini_rag_app.spec
    ```
4.  打包完成后，可执行的应用程序位于 `dist/mini_rag_app` 文件夹内。

## 5. 运行已打包的应用

1.  进入 `dist/mini_rag_app` 文件夹。
2.  双击运行 `mini_rag_app.exe`。
3.  一个控制台窗口将会出现并显示日志。如果一切正常，服务将同样运行在 `http://localhost:8008`。
4.  像在开发模式中一样，测试各个 API 接口。

## 本次 PoC 的关键经验总结

* **`llama-cpp-python` 的打包问题**: 需要谨慎处理其底层的本地库 (native libraries)。在 `.spec` 文件中，将 `llama_cpp\\lib` 目录完整地添加到 `datas` 中是打包成功的关键。

* **`transformers` 的隐藏导入问题**: 像 Qwen3 这样的模型可能会动态导入 PyInstaller 无法自动检测到的模块 (例如 `transformers.models.qwen3`, `transformers.models.qwen3_moe`)。这些模块需要手动添加到 `.spec` 文件的 `hiddenimports` 列表中。

* **数据文件处理 (模型, .env)**: 所有的非代码文件（如模型、配置文件）都必须在 `.spec` 文件的 `datas` 参数中明确指定，才能被捆绑到最终的应用程序中。在代码中使用 `get_resource_path` 这样的辅助函数，对于在源码模式和打包模式下都能正确定位资源至关重要。

* **环境变量处理**: `python-dotenv` 库在开发阶段加载 `.env` 文件非常方便。对于打包后的应用，可以选择将 `.env` 文件一并打包（若无敏感数据），或设计成读取系统环境变量、或外部配置文件。

* **迭代式调试**: 打包复杂应用通常需要经历“构建 -> 测试 -> 发现缺失文件/模块 -> 更新 `.spec` 文件”的多次循环。耐心和细致是成功的关键。

这个 PoC 为未来打包更复杂的 RAG 应用提供了一个坚实的基础和参考。