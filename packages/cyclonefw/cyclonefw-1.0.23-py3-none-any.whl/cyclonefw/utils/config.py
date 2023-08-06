import os
import json
from cyclonefw.core.utils import getLogger

logger = getLogger("config")


class Config(dict):
    """
    配置工具类, 使用方式:

    from cyclonefw.utils import Config

    conf = Config("conf.json")

    conf = Config({
        "data": 123
    })
    
    conf = Config('''{
        "data": 123
    }''')

    print(conf["data"])

    conf.reload()

    print(conf["data"])

    """

    def __init__(self, filenameOrContent):
        """
        创建配置对象
        :param filenameOrContent:
        """
        super(Config, self).__init__(self)
        logger.info("创建配置对象: {}".format(filenameOrContent))
        self.filenameOrContent = filenameOrContent
        self.data = {}
        self.reload()
        pass

    def reload(self):
        """
        配置重载
        :return:
        """
        try:
            if isinstance(self.filenameOrContent, dict):
                self.data = self.filenameOrContent

            if isinstance(self.filenameOrContent, str):
                self.filenameOrContent = self.filenameOrContent.strip()

                if self.filenameOrContent.startswith("{"):
                    self.data = json.loads(self.filenameOrContent)
                    return

                if not os.path.exists(self.filenameOrContent):
                    logger.error("配置文件不存在: {}".format(self.filenameOrContent))
                    self.data = {}
                    return

                with open(self.filenameOrContent, "r") as f:
                    fileContent = f.read()
                    self.data = json.loads(fileContent)
                    return

        except Exception as e:
            logger.error("配置文件载入失败: {}".format(self.filenameOrContent))
            logger.error(e)
        else:
            logger.info("配置载入成功: {}".format(self.data))
        pass

    def __getitem__(self, key):
        """
        获取配置内容
        :param key:
        :return:
        """
        if key in self.data:
            return self.data[key]
        return None
