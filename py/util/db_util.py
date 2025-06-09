from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import declarative_base, sessionmaker
import py.config as config

Base = declarative_base()


class SysInfo(Base):
    # 定义表名
    __tablename__ = 'sys_info'
    # 定义字段
    id = Column(Integer, primary_key=True)
    platform = Column(String(50))
    os_arch = Column(String(50))
    gpu_platform = Column(String(50))
    cpp_version = Column(String(255))
    factory_version = Column(String(255))
    self_version = Column(String(255))


class FileDownload(Base):
    __tablename__ = "file_download"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    model_id = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    type=Column(String(50), nullable=False)
    create_time=Column(TIMESTAMP)
    update_time=Column(TIMESTAMP)



class SqliteSqlalchemy(object):
    def __init__(self):
        # 创建Sqlite连接引擎
        engine = create_engine(config.get_db_url(), echo=True)
        # 创建表
        Base.metadata.create_all(engine)
        # 创建Sqlite的session连接对象
        self.session = sessionmaker(bind=engine)()
