from datetime import date, datetime
from pathlib import PurePosixPath
from time import sleep
from typing import List, Optional, Tuple, Union
from urllib.parse import urlencode, urlunparse
from decouple import config

from requests import get

from borsdata.constants import Calculation, CalculationGroup, PriceType, ReportType
from borsdata.models.branchesrespv1 import BranchesRespV1
from borsdata.models.branchv1 import BranchV1
from borsdata.models.countriesrespv1 import CountriesRespV1
from borsdata.models.countryv1 import CountryV1
from borsdata.models.instrumentsrespv1 import InstrumentsRespV1
from borsdata.models.instrumentupdatedrespv1 import InstrumentUpdatedRespV1
from borsdata.models.instrumentupdatedv1 import InstrumentUpdatedV1
from borsdata.models.instrumentv1 import InstrumentV1
from borsdata.models.kpihistoryv1 import KpiHistoryV1
from borsdata.models.kpimetadatarespv1 import KpiMetadataRespV1
from borsdata.models.kpimetadatav1 import KpiMetadataV1
from borsdata.models.kpisallcomprespv1 import KpisAllCompRespV1
from borsdata.models.kpiscalcupdatedrespv1 import KpisCalcUpdatedRespV1
from borsdata.models.kpishistoryrespv1 import KpisHistoryRespV1
from borsdata.models.kpisrespv1 import KpisRespV1
from borsdata.models.kpissummaryrespv1 import KpisSummaryRespV1
from borsdata.models.kpisummarygroupv1 import KpiSummaryGroupV1
from borsdata.models.kpiv1 import KpiV1
from borsdata.models.marketsrespv1 import MarketsRespV1
from borsdata.models.marketv1 import MarketV1
from borsdata.models.reportmetadatarespv1 import ReportMetadataRespV1
from borsdata.models.reportmetadatav1 import ReportMetadataV1
from borsdata.models.reportscompoundrespv1 import ReportsCompoundRespV1
from borsdata.models.reportsrespv1 import ReportsRespV1
from borsdata.models.reportv1 import ReportV1
from borsdata.models.sectorsrespv1 import SectorsRespV1
from borsdata.models.sectorv1 import SectorV1
from borsdata.models.stockpricedatev1 import StockPriceDateV1
from borsdata.models.stockpricefullv1 import StockPriceFullV1
from borsdata.models.stockpricesdaterespv1 import StockPricesDateRespV1
from borsdata.models.stockpriceslastrespv1 import StockPricesLastRespV1
from borsdata.models.stockpricesrespv1 import StockPricesRespV1
from borsdata.models.stockpricev1 import StockPriceV1
from borsdata.models.stocksplitrespv1 import StockSplitRespV1
from borsdata.models.stocksplitv1 import StockSplitV1
from borsdata.models.translationmetadatarespv1 import TranslationMetadataRespV1
from borsdata.models.translationmetadatav1 import TranslationMetadataV1


class BorsdataAPIClient:
    """API Client for Börsdata.se"""

    def __init__(self, apikey: Optional[str] = None):
        """
        Args:
            apikey (str): API Key for authentication, can also be exported as environment variable BORSDATA_API_KEY.
        """
        if not apikey:
            apikey = config("BORSDATA_API_KEY")
            if not apikey:
                raise Exception("apikey must be specified or exported as an environment variable BORSDATA_API_KEY")

        self._apikey = apikey
        self._api_version = 1
        self._url_schema = "https"
        self._url_host = "apiservice.borsdata.se"
        self._url_base_path = f"v{self._api_version}"
        self._base_params = {"authKey": self._apikey}

    def _get(self, path: str, params: Optional[dict] = None) -> Tuple[int, dict]:
        """Perform a remote request to the API and retries on rate limit responses.

        Args:
            path (str): Path to borsdata api e.g. instruments/kpis/updated, no leading slashes!
            params (Optional[dict], optional): Query parameters to API request. Defaults to None.

        Returns:
            Tuple[int, dict]: First item in tuple is status code from request, the second is data returned from request.
        """

        # Copy base parameters and add api specific params.
        query_params = self._base_params.copy()
        if params:
            query_params.update(params)

        # Construct URL
        url = urlunparse((self._url_schema, self._url_host, str(PurePosixPath(self._url_base_path, path)), None, urlencode(query_params), None))

        while True:
            res = get(url)

            if res.status_code == 200:
                return res.status_code, res.json()

            if res.status_code != 429:
                raise Exception(f"borsdata responded with: {res}")

            sleep(1)

    def get_branches(self) -> List[BranchV1]:
        """Retrives all branches

        Returns:
            list[BranchV1]: List of branches.
        """
        _, data = self._get(path="branches")
        return BranchesRespV1.from_dict(data).branches

    def get_countries(self) -> List[CountryV1]:
        """Retrives all countries

        Returns:
            List[CountryV1]: List of countries.
        """
        _, data = self._get(path="countries")
        return CountriesRespV1.from_dict(data).countries

    def get_markets(self) -> List[MarketV1]:
        """Retrives all markets.

        Returns:
            List[MarketV1]: List of markets.
        """
        _, data = self._get(path="markets")
        return MarketsRespV1.from_dict(data).markets

    def get_sectors(self) -> List[SectorV1]:
        """Retrives all sectors.

        Returns:
            List[SectorV1]: List of sectors.
        """
        _, data = self._get(path="sectors")
        return SectorsRespV1.from_dict(data).sectors

    def get_translation_metadata(self) -> List[TranslationMetadataV1]:
        """Retrives tranlation metadata

        Returns:
            List[TranslationMetadataV1]: List of translation metadata.
        """
        _, data = self._get(path="translationmetadata")
        return TranslationMetadataRespV1.from_dict(data).translation_metadatas

    def get_instruments(self) -> List[InstrumentV1]:
        """Retrives all instruments

        Returns:
            List[InstrumentV1]: List of instruments.
        """
        _, data = self._get(path="instruments")
        return InstrumentsRespV1.from_dict(data).instruments

    def get_instruments_updated(self) -> List[InstrumentUpdatedV1]:
        """Retrives when instruments was last updated.

        Returns:
            List[InstrumentUpdatedV1]: List of instruments when last updated.
        """
        _, data = self._get(path="instruments/updated")
        return InstrumentUpdatedRespV1.from_dict(data).instruments

    def get_kpis_history(self, ins_id: int, kpi_id: int, report_type: ReportType, price_type: PriceType) -> List[KpiHistoryV1]:
        """Retrives a list of kpi data for a given kpi and instrument.

        Args:
            ins_id (int): Id of instrument.
            kpi_id (int): Id of kpi.
            report_type (ReportType): Report type of kpi, i.e. quarter, year, r12.
            price_type (PriceType): Price type of kpi, which price type which is supported depends on the kpi_id.

        Returns:
            List[KpiHistoryV1]: List of kpi history data.
        """
        _, data = self._get(path=f"instruments/{ins_id}/kpis/{kpi_id}/{report_type.value}/{price_type.value}/history")
        return KpisHistoryRespV1.from_dict(data).values

    def get_kpis_summary(self, ins_id: int, report_type: ReportType) -> List[KpiSummaryGroupV1]:
        """Retrives a summary of kpis for a given instrument.

        Args:
            ins_id (int): Id of instrument.
            report_type (ReportType): Report type of kpi, i.e. quarter, year, r12.

        Returns:
            list[KpiSummaryGroupV1]: List of kpi summary groups.
        """
        _, data = self._get(path=f"instruments/{ins_id}/kpis/{report_type.value}/summary")
        return KpisSummaryRespV1.from_dict(data).kpis

    def get_kpis_instrument(self, ins_id: int, kpi_id: int, calculation_group: CalculationGroup,
                            calculation: Calculation) -> KpiV1:
        """Retrives kpi data for a given kpi and instrument.

        Args:
            ins_id (int): Id of instrument.
            kpi_id (int): Id of kpi.
            calculation_group (CalculationGroup): Kpi calculation group, mainly based on time. e.g Calculation.LAST, Calculation.DAY200, Calculation.YEAR7.
            calculation (Calculation): Kpi calculation, e.g. Calculation.LATEST, Calculation.MEAN, Calculation.CAGR.

        Returns:
            KpiV1: Object with kpi data.
        """
        _, data = self._get(path=f"instruments/{ins_id}/kpis/{kpi_id}/{calculation_group.value}/{calculation.value}")
        return KpisRespV1.from_dict(data).value

    def get_kpis_instruments(self, kpi_id: int, calculation_group: Union[str, CalculationGroup],
                             calculation: Union[str, Calculation]) -> List[KpiV1]:
        """Retrives kpi data for a given kpi for all instruments.

        Args:
            kpi_id (int): Id of kpi.
            calculation_group (KpisAllCompRespV1): Kpi calculation group, mainly based on time. e.g Calculation.LAST, Calculation.DAY200, Calculation.YEAR7.
            calculation (Calculation): Kpi calculation, e.g. Calculation.LATEST, Calculation.MEAN, Calculation.CAGR.

        Returns:
            list[KpiV1]: List of kpi data object.
        """
        if not isinstance(calculation_group, CalculationGroup):
            calculation_group = CalculationGroup(calculation_group)
        if not isinstance(calculation, Calculation):
            calculation = calculation(calculation)

        _, data = self._get(path=f"instruments/kpis/{kpi_id}/{calculation_group.value}/{calculation.value}")
        return KpisAllCompRespV1.from_dict(data).values

    def get_kpis_updated(self) -> datetime:
        """Retrives kpis calculation datetime.

        Returns:
            datetime: Datetime when kpis was updated.
        """
        _, data = self._get(path="instruments/kpis/updated")
        datestring = KpisCalcUpdatedRespV1.from_dict(data).kpis_calc_updated
        return datetime.strptime(datestring, r"%Y-%m-%dT%H:%M:%S.%f")

    def get_kpis_metadata(self) -> List[KpiMetadataV1]:
        """Retrives kpi metadata.

        Returns:
            list[KpiMetadataV1]: List of metadata.
        """
        _, data = self._get(path="instruments/kpis/metadata")
        return KpiMetadataRespV1.from_dict(data).kpi_history_metadatas

    def get_reports(self, ins_id: int, max_year=10, max_r12q: int = 10) -> ReportsCompoundRespV1:
        """Retrives reports of all report types for a given instrument.

        Args:
            ins_id (int): Id of instrument.
            max_year (int, optional): Max year report count. Defaults to 10. Max 20.
            max_r12q (int, optional): Max r12 & quarter report count. Defaults to 10. Max 40.

        Returns:
            ReportsCompoundRespV1: Object with three lists of reports, one for each report type.
        """
        _params = {
            "maxYearCount": max_year,
            "maxR12QCount": max_r12q,
        }
        _, data = self._get(path=f"instruments/{ins_id}/reports", params=_params)
        return ReportsCompoundRespV1.from_dict(data)

    def get_reports_r12(self, ins_id: int, max: int = 10) -> List[ReportV1]:
        """Retrives r12 reports for a given instrument.

        Args:
            ins_id (int): Id of instrument.
            max (int, optional): Max report count. Defaults to 10. Max 40.

        Returns:
            list[ReportV1]: List of reports.
        """
        _params = {
            "maxCount": max,
        }
        _, data = self._get(path=f"instruments/{ins_id}/reports/{ReportType.R12.value}", params=_params)
        return ReportsRespV1.from_dict(data).reports

    def get_reports_year(self, ins_id: int, max: int = 10) -> List[ReportV1]:
        """Retrives yearly reports for a given instrument.

        Args:
            ins_id (int): Id of instrument.
            max (int, optional): Max report count. Defaults to 10. Max 20.

        Returns:
            list[ReportV1]: List of reports.
        """

        _, data = self._get(path=f"instruments/{ins_id}/reports/{ReportType.YEAR.value}")
        return ReportsRespV1.from_dict(data).reports

    def get_reports_quarter(self, ins_id: int, max: int = 10) -> List[ReportV1]:
        """Retrives quarterly reports for a given instrument.

        Args:
            ins_id (int): Id of instrument.
            max (int, optional): Max report count. Defaults to 10. Max 40.

        Returns:
            list[ReportV1]: List of reports.
        """
        _, data = self._get(path=f"instruments/{ins_id}/reports/{ReportType.QUARTER.value}")
        return ReportsRespV1.from_dict(data).reports

    def get_reports_metadata(self) -> List[ReportMetadataV1]:
        """Retrives metadata of reports.

        Returns:
            list[ReportMetadataV1]: List of report metadata.
        """
        _, data = self._get(path=f"instruments/reports/metadata")
        return ReportMetadataRespV1.from_dict(data).report_metadatas

    def get_stockprices(self, ins_id: int, start: date, end: date, max: int = 10) -> List[StockPriceV1]:
        """Retrives stock prices for a given instrument within a date range.

        Args:
            ins_id (int): Id of instrument.
            start (date): Start date of stock price.
            end (date): End date of stock price.
            max (int, optional): Max years of stock prices. Defaults to 10. Max 20.

        Returns:
            list[StockPriceV1]: List of stock prices.
        """
        _params = {
            "from": start.isoformat(),
            "to": end.isoformat(),
            "maxCount": max,
        }
        _, data = self._get(path=f"instruments/{ins_id}/stockprices", params=_params)
        return StockPricesRespV1.from_dict(data).stock_prices_list

    def get_stockprices_last(self) -> List[StockPriceFullV1]:
        """Retrives last stock price of all instruments.

        Returns:
            list[StockPriceFullV1]: List of the last stockprice of all instruments.
        """
        _, data = self._get(path=f"instruments/stockprices/last")
        return StockPricesLastRespV1.from_dict(data).stock_prices_list

    def get_stockprices_date(self, _date: date) -> List[StockPriceDateV1]:
        """Retrives stock prices of all instruments for a given date.

        Args:
            _date (date):  Date of stock price.

        Returns:
            list[StockPriceDateV1]: List of stock prices.
        """
        _params = {
            "date": _date.isoformat()
        }
        _, data = self._get(path=f"instruments/stockprices/last", params=_params)
        return StockPricesDateRespV1.from_dict(data).stock_prices_list

    def get_stock_splits(self) -> List[StockSplitV1]:
        """Retrives all stock splits that happend up to a year back.

        Returns:
            list[StockSplitV1]: List of stock splits.§
        """
        _, data = self._get(path=f"instruments/StockSplits")
        return StockSplitRespV1.from_dict(data).stock_split_list
