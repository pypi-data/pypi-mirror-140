from pydantic import BaseModel,validator
from typing import Optional
from datetime import date
from model.common.utils import makeList
from pydantic.class_validators import root_validator
    
class JobofferBase(BaseModel):
    job_title:str
    noc:str
    hours:float
    wage_unit:str
    wage_rate:float
    ot_ratio:float
    permanent:bool
    job_duration:Optional[float]
    job_duration_unit:Optional[str]
    
    @root_validator
    def checkDuration(cls,values):
        if not values.get('permanent') and (not values.get('job_duration') or not values.get('job_duration_unit')):
                raise ValueError("Since it is not permanent job offer, so you have to specify the job duration and job duration unit in info-joboffer sheet")
        return values
    
    @property
    def term(self):
        if self.permanent:
            return "Permanent"
        else:
            if not self.job_duration or not self.job_duration_unit:
                raise ValueError('Since you claimed the job offer is not permanent, you must spcify the job duration and duration unit')
            return str(self.job_duration)+" "+self.job_duration_unit
    
    @property
    def full_part_time(self):
        return "full-time" if self.hours>=30 else 'part-time'
    
    @property
    def salary(self):
        return '{:,.1f}'.format(self.wage_rate) 
    
    @property
    def weekly_hours(self):
        return '{:,.1f}'.format(self.hours)
    
    @property    
    def hourly_rate(self):
        if self.wage_unit=='annually':
            the_rate=self.wage_rate/52/self.hours
        elif self.wage_unit=='monthly':
            the_rate=self.wage_rate*12/52/self.hours
        elif self.wage_unit=='weekly':
            the_rate=self.wage_rate/self.hours
        else: 
            the_rate=self.wage_rate
        return '{0:.4g}'.format(the_rate)

    @property    
    def hourly_rate_say(self):
        return f'${self.hourly_rate} per hour'
    
    @property    
    def overtime_rate(self):
        return float(self.hourly_rate)*self.ot_ratio
    
    @property
    def overtime_rate_say(self):
        return '${rate:,.0f} per hour'.format(rate=float(self.overtime_rate))
    
    @property
    def weekly_rate(self):
        return '{0:.0f}'.format(float(self.hourly_rate)*float(self.weekly_hours))
    
    @property
    def weekly_rate_say(self):
        return '${rate:,.0f} per week'.format(rate=float(self.weekly_rate))
    
    @property
    def monthly_rate(self):
        return '{0:.0f}'.format(float(self.hourly_rate)*float(self.weekly_hours)*52/12)
    
    @property    
    def monthly_rate_say(self):
        return '${rate:,.0f} per month'.format(rate=float(self.monthly_rate))
    
    @property
    def annual_rate(self):
        return '{0:.0f}'.format(float(self.hourly_rate)*float(self.weekly_hours)*52)
    
    @property    
    def annual_rate_say(self):
        return '${rate:,.0f} per year'.format(rate=float(self.annual_rate))
    
    @property
    def requirements(self):
        reqs=[self.specific_edu_requirement,self.skill_experience_requirement,*self.other_requirements]
        return [req for req in reqs if req]