from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker
import py.config as config

Base = declarative_base()


class BaseEntity(Base):
    __abstract__ = True

    create_time = Column(TIMESTAMP, server_default=text("DATETIME(CURRENT_TIMESTAMP, '+8 hours')"))
    update_time = Column(TIMESTAMP, server_default=text("DATETIME(CURRENT_TIMESTAMP, '+8 hours')"),
                         onupdate=text("DATETIME(CURRENT_TIMESTAMP, '+8 hours')"))

    def to_dic(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class SysInfo(BaseEntity):
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


class Model(BaseEntity):
    __tablename__ = 'model'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(50), nullable=False)
    repo = Column(String(50), nullable=False)
    download_platform = Column(String(50))
    files = Column(Text)
    save_dir = Column(String(255))
    import_dir = Column(String(255))


class FileDownload(BaseEntity):
    __tablename__ = "file_download"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    model_id = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)


class SqliteSqlalchemy(object):
    def __init__(self):
        # 创建Sqlite连接引擎
        engine = create_engine(config.get_db_url(), echo=True)
        # 创建表
        Base.metadata.create_all(engine, checkfirst=True)
        # 创建Sqlite的session连接对象
        self.session = sessionmaker(bind=engine)()
