import os
import pathlib
from typing import Optional, Dict
from unittest import TestCase
from unittest.mock import Mock

import click

from montecarlodata.common.common import read_as_json_string
from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.data_lake.events import EventsOnboardingService
from montecarlodata.queries.onboarding import TOGGLE_EVENT_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG, _SAMPLE_DW_ID


class EventsOnboardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = EventsOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    def test_toggle_events_with_no_warehouse(self):
        self._user_service_mock.warehouses = []
        with self.assertRaises(click.exceptions.Abort):
            self._service.toggle_event_configuration()

    def test_toggle_events_with_multiple_warehouses(self):
        self._user_service_mock.warehouses = [{'uuid': _SAMPLE_DW_ID}, {'uuid': _SAMPLE_DW_ID}]
        with self.assertRaises(click.exceptions.Abort):
            self._service.toggle_event_configuration()

    def test_toggle_events_when_successful(self):
        self.assertTrue(self._test_event_toggle(toggle=True))

    def test_toggle_events_with_mapping_file(self):
        mapping_file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'sample_mapping.json')

        options = {'enable': True, 'mapping_file': mapping_file}
        expected_variables = {'enable': True, 'dwId': _SAMPLE_DW_ID, 'mapping': read_as_json_string(mapping_file)}

        self.assertTrue(self._test_event_toggle(options=options, expected_variables=expected_variables))

    def test_toggle_events_when_unsuccessful(self):
        with self.assertRaises(click.exceptions.Abort):
            self._test_event_toggle(toggle=False, success=False)

    def _test_event_toggle(self, toggle: Optional[bool] = True, success: Optional[bool] = True,
                           options: Optional[Dict] = None, expected_variables: Optional[Dict] = None) -> Optional[bool]:
        # Helper to test event toggle with sample configuration
        if not options:
            options = {**_SAMPLE_BASE_OPTIONS, **{'enable': toggle}}
        if not expected_variables:
            expected_variables = {**options, **{'dwId': _SAMPLE_DW_ID}}

        self._user_service_mock.warehouses = [{'uuid': _SAMPLE_DW_ID}]
        self._request_wrapper_mock.convert_snakes_to_camels.return_value = expected_variables
        self._request_wrapper_mock.make_request.return_value = {'toggleEventConfig': {'success': success}}

        status = self._service.toggle_event_configuration(**options)

        self._request_wrapper_mock.convert_snakes_to_camels.assert_called_once_with(expected_variables)
        self._request_wrapper_mock.make_request.assert_called_once_with(
            query=TOGGLE_EVENT_MUTATION,
            variables=expected_variables
        )
        return status
