from typing import ClassVar
from sqlmodel import UUID, Field, Relationship, SQLModel
import datetime
import enum

class Task(SQLModel, table=True):
    """ 
    Task object table
    Each entry represents a new task object

    Fields:
        title: title of the task
        description: description of the task
        completed: boolean whether this task is marked as completed
        deadline: datetime of the task's required complete time
        type: the type of the task
    """

    __tablename__: ClassVar[str] = "tasks"

    id: UUID = Field(
        primary_key=True,
        ondelete="CASCADE"
    )
    title: str = Field(
        max_length=200,
        default=False,
        nullable=False
    )
    description: str = Field(
        max_length=400,
        default=False,
        nullable=False
    )
    completed: bool = Field(
        default=False,
        nullable=False
    )
    deadline: datetime = Field(
        nullable=False,
        defualt=False
    )
    type: enum = Field(
        nullable=False,
        default=False
    )

class TemporalTask(SQLModel, table=True):
    """ 
    TemporalTask object table
    Each entry represents a new temporal task object
    TemporalTask inherits from task by inheritance

    Fields:
        start_date: datetime of the task's ideal scheduled start time
        end_date: datetime of the task's ideal scheduled complete time
        startline: datetime of the task's required start time
        deadline: datetime of the task's required complete time
        schedule_intervals: intervals

    Relationships:
        task_id: the inheritance of task attributes
        intervals: lsit of time intervals for available rescheduling periods
    """

    __tablename__: ClassVar[str] = "temporal_tasks"

    id: UUID = Field(
        primary_key=True,
        ondelete="CASCADE"
    )
    task_id: int = Field(
        foreign_key="tasks.id",
        primary_key=True,
        nullable=False,
    )
    start: datetime = Field(
        default=False,
        nullable=False
    )
    end: datetime = Field(
        default=False,
        nullable=False
    )
    intervals: list["TimeInterval"] = Relationship(
        back_populates="time_intervals"
    )

class TimeInterval(SQLModel, table=True):
    """ 
    TimeInterval object table
    Each entry represents a new time interval 

    Fields:
        start: datetime of the interval's start time
        end: datetime of the interval's complete time

    Relationships:
        task_id: the related temporal task to this time interval
    """

    __tablename__ = "time_intervals"

    id: UUID = Field(
        primary_key=True
    )
    task_id: UUID = Field(
        foreign_key="temporal_tasks.id"
    )
    task: TemporalTask = Relationship(
        back_populates="intervals"
    )
    start: datetime = Field(
        nullable=False,
        default=False
    )
    end: datetime = Field(
        nullable=False,
        default=False
    )

class Event(SQLModel, table=True):
    """ 
    Event object table
    Each entry represents a new event

    Fields:
        task_id: id which relates this event to a task
        goal_value: float abstract value which represents this event's goal value
        routine_value: float abstract value which represents this event's routine value
        personal_value: float abstract value which represents this event's personal value
        relational_value: float abstract value which represents this event's relational value

    Relationships:
        task_id: the related temporal task to this event
    """

    __tablename__ = "events"

    id: UUID = Field(
        primary_key=True
    )
    task_id: UUID = Field(
        foreign_key="tasks.id"
    )
    task: Task = Relationship(
        back_populates="tasks"
    )
    goal_value: float = Field(
        nullable=False,
        default=0.0
    )
    routine_value: float = Field(
        nullable=False,
        default=0.0
    )
    personal_value: float = Field(
        nullable=False,
        default=0.0
    )
    relational_value: float = Field(
        nullable=False,
        default=0.0
    )