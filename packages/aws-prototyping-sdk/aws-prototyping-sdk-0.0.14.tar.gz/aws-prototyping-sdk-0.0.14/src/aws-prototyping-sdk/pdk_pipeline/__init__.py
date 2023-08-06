'''
## pdk_pipeline

TODO
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *


class Greeter(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-prototyping-sdk.pdk_pipeline.Greeter",
):
    '''Example class.'''

    def __init__(self, *, greetee: builtins.str) -> None:
        '''
        :param greetee: 
        '''
        props = GreeterProps(greetee=greetee)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="greet")
    def greet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "greet", []))


@jsii.data_type(
    jsii_type="aws-prototyping-sdk.pdk_pipeline.GreeterProps",
    jsii_struct_bases=[],
    name_mapping={"greetee": "greetee"},
)
class GreeterProps:
    def __init__(self, *, greetee: builtins.str) -> None:
        '''
        :param greetee: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "greetee": greetee,
        }

    @builtins.property
    def greetee(self) -> builtins.str:
        result = self._values.get("greetee")
        assert result is not None, "Required property 'greetee' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GreeterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Greeter",
    "GreeterProps",
]

publication.publish()
