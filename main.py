"""
聚合语录插件

发送各类语录类型获取对应语录
"""

import aiohttp
from loguru import logger
import tomllib
from utils.decorators import *
from utils.plugin_base import PluginBase
from WechatAPI import WechatAPIClient


class YuluPlugin(PluginBase):
    """聚合语录插件类"""
    description = "聚合语录插件：发送语录类型名称获取对应语录"
    author = "鸿菇"
    version = "1.0.0"

    # 语录类型映射字典
    YULU_TYPES = {
        "爱情语录": "1",
        "伤感语录": "2", 
        "励志语录": "3",
        "友情语录": "4",
        "唯美语录": "5",
        "经典语录": "6",
        "搞笑语录": "7",
        "说说语录": "8",
        "心情语录": "9",
        "优美语录": "10",
        "人生语录": "11",
        "伤感语录": "12",
        "非主流语录": "13",
        "个性语录": "14",
        "温柔语录": "15",
        "甜蜜语录": "16"
    }

    API_URL = "https://api.dragonlongzhu.cn/api/yl_juhe.php"
    RENSHE_API = "https://api.dragonlongzhu.cn/api/suiji_renshe.php"

    def __init__(self):
        super().__init__()
        try:
            with open("plugins/YuluPlugin/config.toml", "rb") as f:
                config = tomllib.load(f)
            plugin_config = config["YuluPlugin"]
            self.enable = plugin_config["enable"]
            logger.info(f"[YuluPlugin] 插件初始化完成")
        except Exception as e:
            logger.error(f"[YuluPlugin] 加载配置文件失败: {e}")
            self.enable = False

    @on_text_message(priority=50)
    async def handle_text(self, bot: WechatAPIClient, message: dict):
        """处理文本消息"""
        if not self.enable:
            return True  # 插件未启用，允许后续插件处理

        content = message.get("Content", "").strip()
        from_wxid = message.get("FromWxid", "")
        
        if not content or not from_wxid:
            return True  # 消息内容或发送者ID为空，允许后续插件处理

        # 处理随机人设请求
        if content == "随机人设":
            logger.info(f"[YuluPlugin] 收到随机人设请求")
            result = await self.get_random_character()
            if result:
                await bot.send_text_message(from_wxid, result)
            else:
                await bot.send_text_message(from_wxid, "获取随机人设失败，请稍后再试~")
            return False  # 阻止后续插件处理
            
        # 处理语录请求
        if content in self.YULU_TYPES:
            logger.info(f"[YuluPlugin] 收到语录请求: {content}")
            result = await self.get_yulu(content)
            if result:
                await bot.send_text_message(from_wxid, result)
            else:
                await bot.send_text_message(from_wxid, f"获取{content}失败，请稍后再试~")
            return False  # 阻止后续插件处理
            
        # 处理语录列表请求
        if content == "语录列表":
            types = "、".join(self.YULU_TYPES.keys())
            help_text = f"支持的语录类型：\n{types}\n\n另外可以发送'随机人设'获取随机角色设定"
            await bot.send_text_message(from_wxid, help_text)
            return False  # 阻止后续插件处理
        
        return True  # 不是聚合语录请求，允许后续插件处理

    async def get_yulu(self, yulu_type):
        """获取语录
        
        Args:
            yulu_type: 语录类型
            
        Returns:
            str: 返回语录文本，失败返回None
        """
        try:
            params = {
                "id": self.YULU_TYPES[yulu_type],
                "type": "t(1,text,2,lipson)"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.API_URL, params=params, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.error(f"[YuluPlugin] API请求失败，状态码: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"[YuluPlugin] 获取语录异常: {e}")
            return None

    async def get_random_character(self):
        """获取随机人设
        
        Returns:
            str: 返回随机人设文本，失败返回None
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.RENSHE_API, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.error(f"[YuluPlugin] 随机人设API请求失败，状态码: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"[YuluPlugin] 获取随机人设异常: {e}")
            return None


def get_plugin_class():
    return YuluPlugin
