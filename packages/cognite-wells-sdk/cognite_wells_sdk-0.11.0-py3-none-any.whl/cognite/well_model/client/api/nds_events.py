import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.property_filter import PropertyFilter, filter_to_model
from cognite.well_model.client.models.resource_list import NdsList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DeleteEventSources,
    DistanceRange,
    EventExternalId,
    Nds,
    NdsFilter,
    NdsFilterRequest,
    NdsIngestion,
    NdsIngestionItems,
    NdsItems,
)

logger = logging.getLogger(__name__)


class NdsEventsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, nds_events: List[NdsIngestion]) -> NdsList:
        """Ingest NDS events

        Args:
            nds_events (List[NdsIngestion]): list of Nds events to ingest
        Returns:
            NdsList:
        """
        path = self._get_path("/nds")
        json = NdsIngestionItems(items=nds_events).json()
        response: Response = self.client.post(path, json)
        return NdsList(NdsItems.parse_raw(response.text).items)

    def list(
        self,
        hole_start: Optional[DistanceRange] = None,
        hole_end: Optional[DistanceRange] = None,
        probabilities: Optional[List[int]] = None,
        severities: Optional[List[int]] = None,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        risk_types: PropertyFilter = None,
        subtypes: PropertyFilter = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> NdsList:
        """Get Nds events that matches the filter

        Args:
            hole_start: range of hole start in desired Nds events
            hole_end: range of hole end in desired Nds events
            probabilities: list of interested probabilities
            severities: list of interested severities
            wellbore_asset_external_ids: list of wellbore asset external ids
            wellbore_matching_ids: list of wellbore matching ids
            limit: optional limit. Set to None to get everything
        Returns:
            NdsList:
        """

        def request(cursor, limit):
            nds_filter = NdsFilterRequest(
                filter=NdsFilter(
                    hole_start=hole_start,
                    hole_end=hole_end,
                    probabilities=probabilities,
                    severities=severities,
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                    risk_type=filter_to_model(risk_types),
                    subtype=filter_to_model(subtypes),
                ),
                cursor=cursor,
                limit=limit,
            )

            path: str = self._get_path("/nds/list")
            response: Response = self.client.post(url_path=path, json=nds_filter.json())
            nds_items: NdsItems = NdsItems.parse_raw(response.text)
            return nds_items

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return NdsList(items)

    def delete(self, event_external_ids: List[str]) -> List[str]:
        """Delete NPT events

        Args:
            event_external_ids (List[str]): List of external ids for NDS events

        Returns:
            List[str]: List of external ids for deleted NDS events
        """
        body = DeleteEventSources(items=[EventExternalId(event_external_id=id) for id in event_external_ids])
        path: str = self._get_path("/nds/delete")
        response: Response = self.client.post(url_path=path, json=body.json())
        response_parsed: DeleteEventSources = DeleteEventSources.parse_raw(response.text)
        response_nds_external_ids: List[str] = [e.event_external_id for e in response_parsed.items]
        return response_nds_external_ids

    @staticmethod
    def _get_items(nds_items: NdsItems) -> List[Nds]:
        items: List[Nds] = nds_items.items  # For mypy
        return items

    @staticmethod
    def _get_cursor(nds_items: NdsItems) -> Optional[str]:
        next_cursor: Optional[str] = nds_items.next_cursor  # For mypy
        return next_cursor
