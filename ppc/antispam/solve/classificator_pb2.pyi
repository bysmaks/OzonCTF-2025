from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Nothing(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Token(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class Sample(_message.Message):
    __slots__ = ("uid", "comment")
    UID_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    uid: str
    comment: str
    def __init__(self, uid: _Optional[str] = ..., comment: _Optional[str] = ...) -> None: ...

class SubmitSampleRequest(_message.Message):
    __slots__ = ("token", "uid", "probable_class")
    class Class(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NEGATIVE: _ClassVar[SubmitSampleRequest.Class]
        POSITIVE: _ClassVar[SubmitSampleRequest.Class]
        SPAM: _ClassVar[SubmitSampleRequest.Class]
    NEGATIVE: SubmitSampleRequest.Class
    POSITIVE: SubmitSampleRequest.Class
    SPAM: SubmitSampleRequest.Class
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    PROBABLE_CLASS_FIELD_NUMBER: _ClassVar[int]
    token: Token
    uid: str
    probable_class: SubmitSampleRequest.Class
    def __init__(self, token: _Optional[_Union[Token, _Mapping]] = ..., uid: _Optional[str] = ..., probable_class: _Optional[_Union[SubmitSampleRequest.Class, str]] = ...) -> None: ...

class FlagResult(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
