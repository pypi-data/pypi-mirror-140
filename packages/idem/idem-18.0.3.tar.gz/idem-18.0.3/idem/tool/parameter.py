"""
These classes are used to extract paramaters used inside
SLS files during validation. The code works by simulating
get() function of Python Dictionary object. As we get any
request to access parameter foo using {{ params.get('foo') }}
in SLS file we capture that request sending back a dummy
value, and identifying the parameter name in the process.

To give specific example, a SLS file like this:

    Assure Resource Group Present {{ params.get('rg_name').get('your_rg') }}:
    azure.resource_management.resource_groups.present:
        - resource_group_name: {{ params.get('rg_name').get('your_rg') }}
        - parameters:
            - location{{ params['locations'].get(4).name }}

    Assure Resource Group Present {{ params.get('rg_name').get('my_rg', 'rg') }}:
    azure.resource_management.resource_groups.present:
        - resource_group_name: {{ params.get('rg_name').get('my_rg', 'rg') }}
        - parameters:
            - location{{ params['locations'].get(0).name }}

will produce parameter section like the following in
validate sub command output:

    "parameters": {
        "rg_name": {
            "your_rg": "",
            "my_rg": "rg"
        },
        "locations": [
            {
                "name": ""
            }
        ]
    }

TODO: Implement rest of Python dict functionality in Parameters

"""


class BaseParam:
    def __init__(self, name, display, default) -> None:
        self._name = name
        self._display = display
        self._default = "" if default is None else default
        self._params = {}

    def params(self):
        if not self._params:
            return self._default

        if "*" in self._params:
            return [self._params.get("*").params()]

        ret = {}
        for key, value in self._params.items():
            ret[key] = value.params()

        return ret

    def get(self, param, default):
        pass

    def _set_display(self, display):
        self._display = display

    def __getitem__(self, param):
        return self.get(param)

    def __str__(self) -> str:
        return self._display


class ParamObject(BaseParam):
    def __init__(self, name, display, default) -> None:
        super().__init__(name, display, default)

    def get(self, param, default=None):
        if param in self._params:
            return self._params[param]

        if isinstance(param, int):
            display = self._display + "[" + str(param) + "]"
            if "*" in self._params:
                child = self._params["*"]
                child._set_display(display)
            else:
                child = ParamArray(param, display, default)
                self._params["*"] = child
            return child

        child = ParamObject(param, self._display + "." + param, default)
        self._params[param] = child
        return child


class ParamArray(BaseParam):
    def __init__(self, name, display, default) -> None:
        super().__init__(name, display, default)

    def get(self, param, default=None):
        if param in self._params:
            return self._params[param]

        if isinstance(param, int):
            KeyError("Invalid key type")

        display = "" if self._display == "" else self._display + "."
        child = ParamObject(param, display + self._my_name(param), default)
        self._params[param] = child
        return child

    def _my_name(self, param):
        return param


class Parameters(ParamArray):
    def __init__(self) -> None:
        super().__init__("", "", "")

    def _my_name(self, param):
        return "__" + param + "__"


def get_validate_params(hub):
    return Parameters()
