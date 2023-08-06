from setuptools import setup

name = "types-selenium"
description = "Typing stubs for selenium"
long_description = '''
## Typing stubs for selenium

This is a PEP 561 type stub package for the `selenium` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `selenium`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/selenium. All fixes for
types and metadata should be contributed there.

*Note:* The `selenium` package includes type annotations or type stubs
since version 4.1.2. Please uninstall the `types-selenium`
package if you use this or a newer version.


See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `3afcc1b2b12c8918cbd2541e799f3c95a7e72839`.
'''.lstrip()

setup(name=name,
      version="3.141.8",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/selenium.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['selenium-stubs'],
      package_data={'selenium-stubs': ['__init__.pyi', 'common/__init__.pyi', 'common/exceptions.pyi', 'webdriver/__init__.pyi', 'webdriver/android/__init__.pyi', 'webdriver/android/webdriver.pyi', 'webdriver/blackberry/__init__.pyi', 'webdriver/blackberry/webdriver.pyi', 'webdriver/chrome/__init__.pyi', 'webdriver/chrome/options.pyi', 'webdriver/chrome/remote_connection.pyi', 'webdriver/chrome/service.pyi', 'webdriver/chrome/webdriver.pyi', 'webdriver/common/__init__.pyi', 'webdriver/common/action_chains.pyi', 'webdriver/common/actions/__init__.pyi', 'webdriver/common/actions/action_builder.pyi', 'webdriver/common/actions/input_device.pyi', 'webdriver/common/actions/interaction.pyi', 'webdriver/common/actions/key_actions.pyi', 'webdriver/common/actions/key_input.pyi', 'webdriver/common/actions/mouse_button.pyi', 'webdriver/common/actions/pointer_actions.pyi', 'webdriver/common/actions/pointer_input.pyi', 'webdriver/common/alert.pyi', 'webdriver/common/by.pyi', 'webdriver/common/desired_capabilities.pyi', 'webdriver/common/html5/__init__.pyi', 'webdriver/common/html5/application_cache.pyi', 'webdriver/common/keys.pyi', 'webdriver/common/proxy.pyi', 'webdriver/common/service.pyi', 'webdriver/common/touch_actions.pyi', 'webdriver/common/utils.pyi', 'webdriver/edge/__init__.pyi', 'webdriver/edge/options.pyi', 'webdriver/edge/service.pyi', 'webdriver/edge/webdriver.pyi', 'webdriver/firefox/__init__.pyi', 'webdriver/firefox/extension_connection.pyi', 'webdriver/firefox/firefox_binary.pyi', 'webdriver/firefox/firefox_profile.pyi', 'webdriver/firefox/options.pyi', 'webdriver/firefox/remote_connection.pyi', 'webdriver/firefox/service.pyi', 'webdriver/firefox/webdriver.pyi', 'webdriver/firefox/webelement.pyi', 'webdriver/ie/__init__.pyi', 'webdriver/ie/options.pyi', 'webdriver/ie/service.pyi', 'webdriver/ie/webdriver.pyi', 'webdriver/opera/__init__.pyi', 'webdriver/opera/options.pyi', 'webdriver/opera/webdriver.pyi', 'webdriver/phantomjs/__init__.pyi', 'webdriver/phantomjs/service.pyi', 'webdriver/phantomjs/webdriver.pyi', 'webdriver/remote/__init__.pyi', 'webdriver/remote/command.pyi', 'webdriver/remote/errorhandler.pyi', 'webdriver/remote/file_detector.pyi', 'webdriver/remote/mobile.pyi', 'webdriver/remote/remote_connection.pyi', 'webdriver/remote/switch_to.pyi', 'webdriver/remote/utils.pyi', 'webdriver/remote/webdriver.pyi', 'webdriver/remote/webelement.pyi', 'webdriver/safari/__init__.pyi', 'webdriver/safari/permissions.pyi', 'webdriver/safari/remote_connection.pyi', 'webdriver/safari/service.pyi', 'webdriver/safari/webdriver.pyi', 'webdriver/support/__init__.pyi', 'webdriver/support/abstract_event_listener.pyi', 'webdriver/support/color.pyi', 'webdriver/support/event_firing_webdriver.pyi', 'webdriver/support/events.pyi', 'webdriver/support/expected_conditions.pyi', 'webdriver/support/select.pyi', 'webdriver/support/ui.pyi', 'webdriver/support/wait.pyi', 'webdriver/webkitgtk/__init__.pyi', 'webdriver/webkitgtk/options.pyi', 'webdriver/webkitgtk/service.pyi', 'webdriver/webkitgtk/webdriver.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
