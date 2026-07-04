import pytest
from framework.step import set_phase


class BaseTest:
    @pytest.fixture(autouse=True)
    def lifecycle(self, request):
        # Get test class name and method name from pytest request
        test_class_name = request.cls.__name__ if request.cls else "Unknown"
        test_method_name = request.function.__name__

        # Run setup and let exceptions propagate so pytest marks the correct phase.
        set_phase("Setup", test_class_name, test_method_name)
        self.setup()
        set_phase("Test", test_class_name, test_method_name)
        yield

    @pytest.fixture(autouse=True)
    def _ensure_teardown(self, request):
        # This fixture's finalizer will always run and invoke the test instance's teardown,
        # even if setup or the call raises.
        yield
        test_class_name = request.cls.__name__ if request.cls else "Unknown"
        test_method_name = request.function.__name__
        set_phase("Teardown", test_class_name, test_method_name)
        inst = getattr(request, 'instance', None)
        if inst is not None:
            try:
                inst.teardown()
            except Exception as e:
                request.node._teardown_exc = e
                raise


    def setup(self):
        pass

    def teardown(self):
        pass
    