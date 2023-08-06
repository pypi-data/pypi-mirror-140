import copy
from dataclasses import dataclass

from sust.api.generated.climate_explorer import ApiClient, Configuration
from sust.api.generated.climate_explorer.api import portfolios_api
from sust.api.generated.climate_explorer.model.portfolio_create_request import PortfolioCreateRequest


@dataclass(frozen=True)
class Windows:
    YEARS_5 = 5
    YEARS_15 = 15
    YEARS_30 = 30


@dataclass(frozen=True)
class Scenarios:
    SSP126 = 'ssp126'
    SSP245 = 'ssp245'
    SSP585 = 'ssp585'


@dataclass(frozen=True)
class Hazards:
    CYCLONE = "cyclone"
    WILDFIRE = "wildfire"
    FLOOD_POTENTIAL = "flood_potential"
    WATER_STRESS = "water_stress"
    SEA_LEVEL_RISE = "sea_level_rise"
    HEATWAVE = "heatwave"


@dataclass(frozen=True)
class Indicators:
    EXTREME_PRECIPITATION = "extreme_precip"
    SPEI = "spei_norm"
    INLAND_FLOOD_PROBABILITY = "inland_flood_prob"
    FREQUENCY = "freq"
    OBSERVED_FREQUENCY = "obs_freq"
    CHANGE = "change"
    TEMPERATURE = "temp"
    OBSERVED_SCORE = "obs_score"
    PROBABILITY = "prob"
    BURNED_AREA = "burned_area_norm"
    PRECIPITATION = "precip"


@dataclass(frozen=True)
class Measures:
    LOWER_BOUND = "lb"
    MIDPOINT = "mid"
    UPPER_BOUND = "ub"


class ClimateExplorerClient:
    def __init__(self, api_key, project=None, endpoint=None):
        self._default_req_kwargs = {}
        if project:
            self._default_req_kwargs['project'] = project

        self._openapi_config = Configuration(host=endpoint)
        self._openapi_config.api_key['api_key'] = api_key

        openapi_client = ApiClient(self._openapi_config)
        self._openapi_instance = portfolios_api.PortfoliosApi(openapi_client)

    def _openapi_request(self, request_name, request_args, request_kwargs):
        rk = copy.deepcopy(self._default_req_kwargs)
        rk.update(request_kwargs)
        return getattr(self._openapi_instance, request_name)(*request_args, **rk)

    def _paginated_openapi_request(self, request_name, request_args, request_kwargs):
        rk = copy.deepcopy(self._default_req_kwargs)
        rk.update(request_kwargs)
        return PageIterator(getattr(self._openapi_instance, request_name), request_args, rk)

    def portfolios(self):
        #NOTE(bcwaldon): this should be paginated, but is not yet implemented in the API
        it = self._openapi_request('portfolios_list', (), {})
        return (Portfolio(self, obj) for obj in it)

    def create(self, portfolio_name):
        req = PortfolioCreateRequest(portfolio_name)
        obj = self._openapi_request('portfolios_create', (req,), {})
        return Portfolio(self, obj)

    def upload_assets(self, portfolio_name, assets_path):
        file = open(assets_path, "rb")
        obj = self._openapi_request('portfolios_assets_import_create', (portfolio_name, file), {})
        return obj

    def portfolio(self, portfolio_name):
        obj = self._openapi_request('portfolios_read', (portfolio_name,), {})
        return Portfolio(self, obj)


class Portfolio:
    def __init__(self, client, obj):
        self._client = client
        self._obj = obj
        self.name = obj["portfolio_name"]

    def __getitem__(self, key):
        return self._obj[key]

    def assets(self, labels=None):
        it = self._client._paginated_openapi_request('portfolios_assets_list', (self._obj['portfolio_name'],), {})

        objects = [
            obj for obj in it if
              (labels == None or all(obj['labels'].get(k) == v for k, v in labels.items()))
        ]

        return AssetList(self, objects)

    def physical_risk_timeseries(self, scenario=None, hazard=None, indicator=None, measure=None, page_size=None):
        req_kwargs = {}
        if scenario:
            req_kwargs['scenario'] = scenario
        if hazard:
            req_kwargs['hazard'] = hazard
        if indicator:
            req_kwargs['indicator'] = indicator
        if measure:
            req_kwargs['measure'] = measure
        if page_size:
            req_kwargs['rows'] = page_size

        it = self._client._paginated_openapi_request('portfolios_datasets_physical_items_list', (self.name,), req_kwargs)

        objects = []
        for obj in it:
            obj_d = obj.to_dict()
            re = obj_d.pop('risk_exposure')
            obj_d.update(re)
            objects.append(obj_d)

        return PhysicalRiskTimeseriesList(objects)

    def physical_risk_summary(self, scenario=None, hazard=None, window=None, page_size=None):
        req_kwargs = {}
        if scenario:
            req_kwargs['scenario'] = scenario
        if hazard:
            req_kwargs['hazard'] = hazard
        if window:
            req_kwargs['window'] = window
        if page_size:
            req_kwargs["rows"] = page_size

        it = self._client._paginated_openapi_request('portfolios_datasets_physical_summary_list', (self.name,), req_kwargs)
        objects = []
        for obj in it:
            obj_d = obj.to_dict()
            summaries = obj_d.pop('risk_summaries')
            for summary in summaries:
                summary.update(obj_d)
                objects.append(summary)

        return PhysicalRiskSummaryList(objects)


class AssetList:
    def __init__(self, portfolio, objects):
        self._portfolio = portfolio
        self._objects = objects
        self._index = dict((obj['portfolio_index'], obj) for obj in objects)

    def to_dicts(self):
        return [obj.to_dict() for obj in self._objects]

    def physical_risk_timeseries(self, **kwargs):
        lst = self._portfolio.physical_risk_timeseries(**kwargs)
        filtered = [do for do in lst.to_dicts() if do['portfolio_index'] in self._index]
        return PhysicalRiskTimeseriesList(filtered)

    def physical_risk_summary(self, **kwargs):
        lst = self._portfolio.physical_risk_summary(**kwargs)
        filtered = [do for do in lst.to_dicts() if do['portfolio_index'] in self._index]
        return PhysicalRiskSummaryList(filtered)


class PhysicalRiskTimeseriesList:
    def __init__(self, dict_objects):
        self._dict_objects = dict_objects

    def to_dicts(self):
        return self._dict_objects


class PhysicalRiskSummaryList:
    def __init__(self, dict_objects):
        self._dict_objects = dict_objects

    def to_dicts(self):
        return self._dict_objects


class PageIterator:
    def __init__(self, req_func, req_args, req_kwargs):
        self.req_func = req_func
        self.req_args = req_args
        self.req_kwargs = req_kwargs

        self.req_kwargs['page'] = 1
        self.req_kwargs.setdefault('rows', 100)

        self.cache = []
        self.exhausted = False

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.cache) == 0 and not self.exhausted:
            resp = self.req_func(*self.req_args, **self.req_kwargs)
            self.cache = resp

            if len(resp) < self.req_kwargs['rows']:
                self.exhausted = True
            else:
                self.req_kwargs['page'] = self.req_kwargs['page'] + 1

        if len(self.cache) > 0:
            return self.cache.pop(0)

        raise StopIteration
