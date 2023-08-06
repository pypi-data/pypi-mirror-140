import typing as t
from copy import deepcopy

from sqlalchemy import create_engine
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


class CloudSQL_BQ_Wrapper:
    engine: Engine = None
    declarative_base: DeclarativeMeta = None
    ProfileURLClass = None

    def __init__(
        self,
        db_host: str = "",
        db_port: t.Union[str, int] = "",
        db_name: str = "",
        db_username: str = "",
        db_password: str = "",
        urls_table_name: str = "",
        bq_dataset_name: str = "",
        gcp_project: str = "",
        gcp_credentials_path: str = "",
        use_bigquery: bool = False
    ):
        self.URLS_TABLE_NAME = bq_urls_table_name

        # SQL db
        self.DB_HOST = db_host
        self.DB_PORT = db_port
        self.DB_NAME = db_name
        self.DB_USERNAME = db_username
        self.DB_PASSWORD = db_password
        db_params = [db_host, db_port, db_name, db_username, db_password]

        # BigQuery
        self.BQ_DATASET_NAME = bq_dataset_name
        self.GCP_PROJECT = gcp_project
        self.GCP_CREDENTIALS_PATH = gcp_credentials_path
        bq_params = [bq_dataset_name, gcp_project, gcp_credentials_path]

        if use_bigquery and not all(bq_params):
            raise Exception(
                f"All of {', '.join(bq_params)} must be supplied"
                f" to connect to BigQuery"
            )
        elif not all(db_params):
            raise Exception(
                f"All of {', '.join(db_params)} must be supplied"
                f" to use Postgres Engine"
            )

        self.engine = self._create_engine(use_bigquery)
        self.declarative_base = declarative_base()

    def _create_engine(self, use_bigquery=False) -> Engine:
        if use_bigquery:
            kwargs = {"url": f"bigquery://{self.GCP_PROJECT}/{self.BQ_DATASET_NAME}"}
            if self.GCP_CREDENTIALS_PATH:
                kwargs["credentials_path"] = self.GCP_CREDENTIALS_PATH
        else:
            kwargs = {
                "url": "postgresql+pg8000://{}:{}@{}:{}/{}".format(
                    self.DB_USERNAME, self.DB_PASSWORD, self.DB_HOST,
                    str(self.DB_PORT), self.DB_NAME
                )
            }
        engine = create_engine(**kwargs)
        return engine

    def get_declarative_base(self):
        return self.declarative_base

    def get_query_property(self):
        session = scoped_session(sessionmaker(bind=self.engine))
        return session.query_property()

    def update_master_list(
        self,
        profile_url: str,
        job_title: str,
        location: str,
        pdf_hash: str = None,
        pdf_bytesize: str = None,
        pdf_stage: bool = None,
        json_stage: bool = None,
        processor_stage: bool = None,
        success: bool = None,
        create_if_absent: bool = False
    ):
        attrs = {
            "pdf_hash": pdf_hash,
            "pdf_bytesize": pdf_bytesize,
            "pdf_stage": pdf_stage,
            "json_stage": json_stage,
            "processor_stage": processor_stage,
            "success": success
        }
        reqd_attrs = deepcopy(attrs)
        [reqd_attrs.pop(x) for x in ("pdf_hash", "pdf_bytesize")]
        if not list(filter(lambda x: x is not None, reqd_attrs.values())):
            raise Exception(
                f"You must supply one of {list(attrs.keys())}"
            )
        if not self.ProfileURLClass:
            raise Exception("To use this feature, call `create_models`"
                            " and `create_tables_in_db` first")

        _query = self.ProfileURLClass.query\
            .filter_by(linkedin_url=profile_url)\
            .filter_by(job_title=job_title)\
            .filter_by(location=location)
        url_obj = _query.first()

        if (not url_obj) and create_if_absent:
            url_obj = self.ProfileURLClass(
                linkedin_url=profile_url, job_title=job_title,
                location=location
            )
        elif not url_obj:
            raise Exception(
                f"Profile URL {profile_url} does not exist in "
                f"LWC Table. Call again with `create_if_absent=True` "
                f"to add")

        for attr, value in attrs.items():
            if value is not None:
                setattr(url_obj, attr, value)
        session = self.ProfileURLClass.query.session
        session.add(url_obj)
        session.commit()
        session.close()

    def create_models(self):
        """Override this method to create custom tables"""
        reqd = (self.URLS_TABLE_NAME)
        if not all(reqd):
            raise Exception(
                'Attribute "URLS_TABLE_NAME" should be set to use this'
                ' feature'
            )
        query_property = self.get_query_property()

        class ProfileURL(self.declarative_base):
            __tablename__: str = self.URLS_TABLE_NAME
            url_id: str = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
            linkedin_url: str = Column(Text)
            job_title: str = Column(Text)
            location: str = Column(Text)
            pdf_hash: t.Optional[str] = Column(Text, nullable=True)
            pdf_bytesize: t.Optional[str] = Column(Text, nullable=True)
            pdf_stage: t.Optional[bool] = Column(Boolean, nullable=True)
            json_stage: t.Optional[bool] = Column(Boolean, nullable=True)
            processor_stage: t.Optional[bool] = Column(Boolean, nullable=True)
            success: t.Optional[bool] = Column(Boolean, nullable=True)
            query = query_property

            def dict(self) -> t.Dict:
                retval = {
                    "url_id": self.url_id,
                    "linkedin_url": self.linkedin_url,
                    "job_title": self.job_title,
                    "location": self.location,
                    "pdf_hash": self.pdf_hash,
                    "pdf_bytesize": self.pdf_bytesize,
                    "pdf_stage": self.pdf_stage,
                    "json_stage": self.json_stage,
                    "processor_stage": self.processor_stage,
                    "success": self.success
                }
                return retval

        self.ProfileURLClass = ProfileURL
        return ProfileURL

    def create_tables_in_db(self):
        self.declarative_base.metadata.create_all(self.engine)
