from typing import ClassVar
from sqlmodel import UUID, Field, Relationship, SQLModel
from datetime import datetime, timedelta
import enum

class TaskType(str, enum.Enum):
    TASK = "task"
    TEMPORALTASK = "temporal_task"
    ROUTINE = "routine"
    GOAL = "goal"

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

    __tablename__ = "tasks"

    id: UUID = Field(
        primary_key=True,
        ondelete="CASCADE"
    )
    title: str = Field(
        max_length=200,
        nullable=False
    )
    description: str = Field(
        max_length=400,
        nullable=False
    )
    completed: bool = Field(
        nullable=False
    )
    deadline: datetime = Field(
        nullable=False,
    )
    type: TaskType = Field(
        nullable=False,
    )

    events: list["Event"] = Relationship(
        back_populates="task"
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

    __tablename__ = "temporal_tasks"

    task_id: UUID = Field(
        foreign_key="tasks.id",
        primary_key=True,
        nullable=False,
    )
    start: datetime = Field(
        nullable=False
    )
    end: datetime = Field(
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
    start: datetime = Field(
        nullable=False,
    )
    end: datetime = Field(
        nullable=False,
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
        task_id: the related task to this event
    """

    __tablename__ = "events"

    id: UUID = Field(
        primary_key=True
    )
    task_id: UUID = Field(
        foreign_key="tasks.id"
    )
    goal_value: float = Field(
        nullable=False,
    )
    routine_value: float = Field(
        nullable=False,
    )
    personal_value: float = Field(
        nullable=False,
    )
    relational_value: float = Field(
        nullable=False,
    )

    task: Task = Relationship(
        back_populates="events"
    )

class Goal(SQLModel, table=True):
    """ 
    Goal object table
    Each entry represents a new goal

    Fields:
        task_id: id which relates this goal to a task
        subgoals: list of subgoals for this goal
        completed_steps: the number of completed steps

    Relationships:
        task_id: the related temporal task to this goal
        subgoals: the list of task ids for the subgoals
    """

    __tablename__ = "goals"

    task_id: UUID = Field(
        foreign_key="tasks.id",
        primary_key=True,
        nullable=False,
    )
    completed_steps: int = Field(
        nullable=False,
    )

    subgoals: list["Task"] = Relationship(
        back_populates="tasks"
    )

class RoutineEntry(SQLModel, table=True):
    """ 
    RoutineEntry object table
    Each entry represents a new routine entry object

    Fields:
        task_id: the associated task for this entry
        duration: the time duration this task should take to complete

    Relationships:
        task_id: the inheritance of task attributes
    """

    __tablename__: ClassVar[str] = "routine_entries"

    id: UUID = Field(
        primary_key=True,
        ondelete="CASCADE"
    )
    task_id: UUID = Field(
        foreign_key="tasks.id",
        nullable=False,
    )
    duration: timedelta = Field(
        nullable=False
    )

class Routine(SQLModel, table=True):
    """ 
    Routine object table
    Each entry represents a new routine object

    Fields:
        task_id: the associated task for this entry
        duration: the time duration this task should take to complete

    Relationships:
        task_id: the inheritance of task attributes
    """

    __tablename__: ClassVar[str] = "routines"

    task_id: UUID = Field(
        foreign_key="tasks.id",
        primary_key=True,
        nullable=False,
    )
    duration: timedelta = Field(
        nullable=False
    )