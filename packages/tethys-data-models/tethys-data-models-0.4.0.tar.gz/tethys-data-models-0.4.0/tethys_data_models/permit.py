#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 14:10:31 2021

@author: mike
"""
from datetime import datetime, date
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
from enum import Enum
import orjson
from .utils import orjson_dumps
from .geometry import geometry
from . import base

#########################################
### Models


class Period(str, Enum):
    seconds = 'S'
    hours = 'H'
    days = 'D'
    weeks = 'W'
    months = 'M'
    years = 'Y'


class Units(str, Enum):
    liters = 'l'
    cubic_meters = 'm3'


class LimitBoundary(str, Enum):
    min = 'min'
    max = 'max'


class AggregationStat(str, Enum):
    min = 'min'
    max = 'max'
    median = 'median'
    mean = 'mean'


class Limit(BaseModel):
    """

    """
    value: Union[int, float]
    period: Period
    units: Units
    limit_boundary: LimitBoundary
    aggregation_stat: Optional[AggregationStat]


class ConditionType(str, Enum):
    abstraction_limit = 'abstraction limit'


class Condition(BaseModel):
    """

    """
    condition_type: ConditionType
    limit: Optional[List[Limit]]
    text: Optional[str]


class ActivityType(str, Enum):
    consumptive_take_water = 'consumptive take water'
    non_consumptive_take_water = 'non-consumptive take water'
    divert_water = 'divert water'
    dam_water = 'dam water'
    use_water = 'use water'
    discharge_water = 'discharge water'


class SdMethod(str, Enum):
    """
    The stream depletion method assigned for the permit.
    """
    theis_1941 = 'theis_1941'
    hunt_1999 = 'hunt_1999'
    hunt_2003 = 'hunt_2003'
    hunt_2009 = 'hunt_2009'
    ward_lough_2011 = 'ward_lough_2011'


class AquiferProp(BaseModel):
    """

    """
    method: Optional[SdMethod]
    stream_depletion_ratio: Optional[float] = Field(None, description='The stream depletion ratio calculated from the n_days and the method.')
    n_days: Optional[int] = Field(None, description='The number of pumping days assigned to the permit associated with the stream depletion calculation requirements.')
    sep_distance : Optional[int] = Field(None, description='The separation distance from the pumped well to the stream.')
    pump_aq_trans : Optional[int] = Field(None, description='The pumped (confined) aquifer transmissivity (m2/day).')
    pump_aq_s : Optional[float] = Field(None, description='The storage coefficient of the pumped aquifer.')
    upper_aq_trans: Optional[int] = Field(None, description='The surficial aquifer transmissivity (m2/day).')
    upper_aq_s : Optional[float] = Field(None, description='The storage coefficient of the surficial aquifer.')
    lower_aq_trans: Optional[int] = Field(None, description='The confined aquifer transmissivity (m2/day).')
    lower_aq_s : Optional[float] = Field(None, description='The storage coefficient (specific storage) of the confined aquifer.')
    aqt_k : Optional[float] = Field(None, description='The aquitard hydraulic conductivity (m/day).')
    aqt_s : Optional[float] = Field(None, description='The aquitard storage coefficient.')
    aqt_thick : Optional[int] = Field(None, description='The aquitard vertical thickness (m).')
    stream_k : Optional[float] = Field(None, description='Streambed hydraulic conductivity (m/day).')
    stream_thick : Optional[int] = Field(None, description='The streambed vertical thickness (m).')
    stream_width : Optional[int] = Field(None, description='The streambed width (m).')


class Station(base.Station):
    """
    Contains the station data.
    """
    properties: AquiferProp


class Feature(str, Enum):
    surface_water = 'surface water'
    groundwater = 'groundwater'


class Activity(BaseModel):
    """

    """
    activity_type: ActivityType
    feature: Feature
    primary_purpose: Optional[str]
    station: List[Station]
    condition: List[Condition]


class Status(str, Enum):
    expired = 'Expired'
    surrendered = 'Surrendered'
    active = 'Active'
    archived = 'Archived'
    lapsed = 'Lapsed'
    superseded = 'Superseded'
    cancelled = 'Cancelled'
    expired_124 = 'Expired - S.124 Protection'


class PermitType(str, Enum):
    water_permit = 'water permit'


class Permit(BaseModel):
    """

    """
    permit_id: str
    status: Status
    status_changed_date: Optional[date]
    commencement_date: date
    expiry_date: date
    effective_end_date: Optional[date]
    exercised: bool
    permitting_authority: str
    permit_type: PermitType
    activity: Activity
    modified_date: datetime = Field(..., description='The modification date of the last edit.')

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps



##########################################
### Export json schema

# with open('/media/nvme1/git/nz-rma-permits/nzpermits/tests/permit_schema.json', 'w') as f:
#     f.write(Permit.schema_json())
