from mock import patch

from .test_helper import (
    raises, patch_open
)

from kiwi.runtime_config import RuntimeConfig
from kiwi.exceptions import KiwiRuntimeConfigFormatError
from kiwi.defaults import Defaults


class TestRuntimeConfig:
    def setup(self):
        with patch.dict('os.environ', {'HOME': '../data'}):
            self.runtime_config = RuntimeConfig()

        # pretend that none of the runtime config files exist, even if they do
        # (e.g. the system wide config file in /etc/kiwi.yml)
        # => this will give us the defaults
        with patch('os.path.exists', return_value=False):
            self.default_runtime_config = RuntimeConfig()

    @patch('os.path.exists')
    @patch('yaml.safe_load')
    def test_reading_system_wide_config_file(self, mock_yaml, mock_exists):
        exists_call_results = [True, False]

        def os_path_exists(config):
            return exists_call_results.pop()

        mock_exists.side_effect = os_path_exists
        with patch_open as mock_open:
            self.runtime_config = RuntimeConfig()
            mock_open.assert_called_once_with('/etc/kiwi.yml', 'r')

    @raises(KiwiRuntimeConfigFormatError)
    def test_invalid_yaml_format(self):
        self.runtime_config.config_data = {'xz': None}
        self.runtime_config.get_xz_options()

    def test_get_xz_options(self):
        assert self.runtime_config.get_xz_options() == ['-a', '-b', 'xxx']

    def test_is_obs_public(self):
        assert self.runtime_config.is_obs_public() is True

    def test_get_bundle_compression(self):
        assert self.runtime_config.get_bundle_compression() is True

    def test_get_bundle_compression_default(self):
        assert self.default_runtime_config.get_bundle_compression(default=True) is True
        assert self.default_runtime_config.get_bundle_compression(default=False) is False

    def test_is_obs_public_default(self):
        assert self.default_runtime_config.is_obs_public() is True

    def test_get_obs_download_server_url(self):
        assert self.runtime_config.get_obs_download_server_url() == \
            'http://example.com'

    def test_get_obs_download_server_url_default(self):
        assert self.default_runtime_config.get_obs_download_server_url() == \
            Defaults.get_obs_download_server_url()

    def test_get_container_compression(self):
        assert self.runtime_config.get_container_compression() is None

    def test_get_container_compression_default(self):
        assert self.default_runtime_config.get_container_compression() == 'xz'

    @patch.object(RuntimeConfig, '_get_attribute')
    @patch('kiwi.logger.log.warning')
    def test_get_container_compression_invalid(
        self, mock_warning, mock_get_attribute
    ):
        mock_get_attribute.return_value = 'foo'
        assert self.runtime_config.get_container_compression() == 'xz'
        mock_warning.assert_called_once_with(
            'Skipping invalid container compression: foo'
        )

    @patch.object(RuntimeConfig, '_get_attribute')
    def test_get_container_compression_xz(self, mock_get_attribute):
        mock_get_attribute.return_value = 'xz'
        assert self.runtime_config.get_container_compression() == 'xz'

    def test_get_iso_tool_category(self):
        assert self.runtime_config.get_iso_tool_category() == 'cdrtools'

    def test_get_iso_tool_category_default(self):
        assert self.default_runtime_config.get_iso_tool_category() == 'xorriso'

    @patch.object(RuntimeConfig, '_get_attribute')
    @patch('kiwi.logger.log.warning')
    def test_get_iso_tool_category_invalid(
        self, mock_warning, mock_get_attribute
    ):
        mock_get_attribute.return_value = 'foo'
        assert self.runtime_config.get_iso_tool_category() == 'xorriso'
        mock_warning.assert_called_once_with(
            'Skipping invalid iso tool category: foo'
        )

    def test_get_oci_archive_tool(self):
        assert self.runtime_config.get_oci_archive_tool() == 'umoci'

    def test_get_oci_archive_tool_default(self):
        assert self.default_runtime_config.get_oci_archive_tool() == 'umoci'

    def test_get_disabled_runtime_checks(self):
        assert self.runtime_config.get_disabled_runtime_checks() == [
            'check_dracut_module_for_oem_install_in_package_list',
            'check_container_tool_chain_installed'
        ]
