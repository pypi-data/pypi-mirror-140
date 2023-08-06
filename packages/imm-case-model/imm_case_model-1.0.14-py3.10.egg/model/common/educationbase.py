from pydantic import BaseModel,validator
from datetime import date
from typing import Optional
from model.common.mixins import DurationMixin
from model.common.utils import makeList,normalize

"""
with properties of start_from and end_to got from mixin
"""
class EducationBase(BaseModel,DurationMixin):
    start_date: date
    end_date:Optional[date]
    school_name: str
    education_level:str
    field_of_study:str
    
    _normalize_school_name=validator('school_name',allow_reuse=True,check_fields=False)(normalize)
    _normalize_field_of_study=validator('field_of_study',allow_reuse=True,check_fields=False)(normalize)
    
    @validator("end_date")
    def endDateBigger(cls,end_date,values):
        start_date=values.get('start_date')
        the_date=end_date if end_date else date.today()
        if (the_date-start_date).days<=0:
            raise ValueError(f'End date {the_date} is earlier than start date {start_date}')
        end_date=end_date if end_date else "Present"
        return end_date
