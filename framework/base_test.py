import pytest
from framework.step import set_phase


class BaseTest:

    @pytest.fixture(autouse=True)
    def lifecycle(self, request):
        # Get test class name and method name from pytest request
        test_class_name = request.cls.__name__ if request.cls else "Unknown"
        test_method_name = request.function.__name__
        
        set_phase("Setup", test_class_name, test_method_name)
        self.setup()
        set_phase("Test", test_class_name, test_method_name)
        yield
        set_phase("Teardown", test_class_name, test_method_name)
        self.teardown()

    def setup(self):
        pass

    def teardown(self):
        pass
    