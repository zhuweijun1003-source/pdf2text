"""
AI摘要功能测试脚本
用于验证DeepSeek API集成是否正常工作
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("AI摘要功能检查")
print("=" * 60)
print()

# 1. 检查配置
print("[1/4] 检查配置...")
from config import Config

api_key = Config.DEEPSEEK_API_KEY
if api_key and api_key != 'your_deepseek_api_key_here':
    print(f"✅ API密钥已配置 (长度: {len(api_key)})")
else:
    print("❌ API密钥未配置")
    print("   请在 .env 文件中设置 DEEPSEEK_API_KEY")
    exit(1)

print(f"✅ API基础URL: {Config.DEEPSEEK_BASE_URL}")
print(f"✅ 模型: {Config.DEEPSEEK_MODEL}")
print()

# 2. 检查依赖
print("[2/4] 检查依赖...")
try:
    import requests
    print("✅ requests 已安装")
except ImportError:
    print("❌ requests 未安装")
    exit(1)

try:
    from loguru import logger
    print("✅ loguru 已安装")
except ImportError:
    print("❌ loguru 未安装")
    exit(1)

print()

# 3. 测试API连接
print("[3/4] 测试API连接...")
try:
    from deepseek_client import DeepSeekClient
    
    # 初始化客户端
    client = DeepSeekClient()
    print("✅ DeepSeek客户端初始化成功")
    
except ValueError as e:
    print(f"❌ 客户端初始化失败: {e}")
    exit(1)
except Exception as e:
    print(f"❌ 未知错误: {e}")
    exit(1)

print()

# 4. 测试摘要功能（可选，需要联网）
print("[4/4] 测试文本摘要功能...")
print("是否要测试实际的API调用？这将消耗少量API配额。")
test_api = input("输入 'y' 继续测试，或按Enter跳过: ").lower().strip()

if test_api == 'y':
    try:
        test_text = """人工智能（Artificial Intelligence, AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大，可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。人工智能可以对人的意识、思维的信息过程的模拟。人工智能不是人的智能，但能像人那样思考、也可能超过人的智能。"""
        print(f"\n原始文本: {test_text[:100]}...")
        print("\n正在调用API生成摘要...")
        
        summary = client.summarize_text(
            test_text,
            length='short'
        )
        
        print(f"✅ API调用成功！")
        print(f"生成的摘要: {summary}")
        
    except Exception as e:
        print("❌ API调用失败: {e}")
        print("\n可能的原因:")
        print("1. API密钥无效")
        print("2. 网络连接问题")
        print("3. API配额已用完")
        print("4. API服务暂时不可用")
else:
    print("⏭️  跳过API调用测试")

print()
print("=" * 60)
print("检查完成！")
print("=" * 60)
print()

# 总结
print("📋 总结:")
print("1. ✅ 配置文件正常")
print("2. ✅ 依赖已安装")
print("3. ✅ 客户端可初始化")

if test_api == 'y':
    print("4. 检查上方API调用结果")
else:
    print("4. ⏭️  未测试API调用")

print()
print("💡 在Streamlit应用中使用AI摘要的步骤:")
print("   1. 上传并处理PDF文件")
print("   2. 在文本内容标签页点击 '🤖 生成文本摘要'")
print("   3. 输入API密钥（如果未在.env中配置）")
print("   4. 选择摘要长度")
print("   5. 点击 '▶️ 生成摘要'")
print()
