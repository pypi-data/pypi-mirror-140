# PhysicalRiskDatasetItemResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**portfolio_name** | **str** | Name of the corresponding portfolio | 
**portfolio_index** | **int** | Portfolio-scoped index of the asset | 
**entity_id** | **str** | ID of the asset | 
**entity_name** | **str** | Name of the asset | 
**hazard** | **str** | Climate hazard | 
**indicator** | **str** | Risk indicator | 
**measure** | **str** | Indicator measure (e.g. upper bound (ub), lower bound (lb), or mean/median (mid) | 
**risk_exposure** | **{str: (float,)}** | Timeseries risk exposure data. Projected exposure data is bucketed by year (keys formatted YYYY). Observational data is bucketed by month (keys formatted YYYY-MM). | 
**scenario** | **str** | Climate scenario | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


