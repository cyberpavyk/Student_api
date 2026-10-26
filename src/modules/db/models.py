from datetime import datetime, date
from typing import Optional


from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    MetaData,
    SmallInteger,
    String,
    Table,
    false,
    func,
)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    relationship,
    configure_mappers,
)

from modules.config.config import config

from modules.models.enums import UserStatus, ProfessorStatus

engine = create_async_engine(
    url=config.urlconfig(), echo=config.debug, pool_size=10, max_overflow=20
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    # convention for postgresql naming
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


# Mixins for code shortening
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class PersonMixin:
    name: Mapped[str] = mapped_column(String(64))
    surname: Mapped[str] = mapped_column(String(64))
    patronymic: Mapped[Optional[str]] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(64), unique=True)


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        server_default=false(),
        index=True,
    )


# Student subjects table
student_subject = Table(
    "student_subject",
    Base.metadata,
    Column(
        "student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "subject_id", ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Student(TimestampMixin, SoftDeleteMixin, PersonMixin, Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)

    status: Mapped[UserStatus]
    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL"), index=True
    )

    group: Mapped[Optional["Group"]] = relationship(back_populates="students")
    subjects: Mapped[list["Subject"]] = relationship(
        secondary=student_subject,
        back_populates="students",
    )
    grades: Mapped[list["Grade"]] = relationship(back_populates="student")

    def __repr__(self) -> str:
        return f"Student(id={self.id}, username={self.username!r})"


class Group(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(64))
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"), index=True)
    faculty: Mapped["Faculty"] = relationship(back_populates="groups")
    students: Mapped[list["Student"]] = relationship(back_populates="group")


class Professor(PersonMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "professors"

    id: Mapped[int] = mapped_column(primary_key=True)

    subjects: Mapped[list["Subject"]] = relationship(back_populates="professor")
    status: Mapped[ProfessorStatus]


class Faculty(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(128), unique=True)
    groups: Mapped[list["Group"]] = relationship(back_populates="faculty")


class Subject(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "subjects"

    __table_args__ = (CheckConstraint("hours_per_semester > 0", name="hours_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(256))
    hours_per_semester: Mapped[int]

    professor_id: Mapped[int] = mapped_column(ForeignKey("professors.id"), index=True)
    professor: Mapped["Professor"] = relationship(back_populates="subjects")
    students: Mapped[list["Student"]] = relationship(
        secondary=student_subject, back_populates="subjects"
    )

    grades: Mapped[list["Grade"]] = relationship(back_populates="subject")


class Grade(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "grades"
    __table_args__ = (CheckConstraint("value BETWEEN 1 AND 5", name="value_range"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    value: Mapped[int] = mapped_column(SmallInteger)
    graded_at: Mapped[date] = mapped_column(Date)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), index=True
    )

    student: Mapped["Student"] = relationship(back_populates="grades")
    subject: Mapped["Subject"] = relationship(back_populates="grades")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


configure_mappers()
