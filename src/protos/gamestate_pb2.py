# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: gamestate.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fgamestate.proto\"\"\n\tGameState\x12\x15\n\x05state\x18\x01 \x01(\x0e\x32\x06.State*T\n\x05State\x12\x0e\n\nPOISON_IVY\x10\x00\x12\x0f\n\x0b\x44\x45HYDRATION\x10\x01\x12\x15\n\x11HYPOTHERMIA_START\x10\x02\x12\x13\n\x0fHYPOTHERMIA_END\x10\x03\x42\x02H\x03\x62\x06proto3')

_STATE = DESCRIPTOR.enum_types_by_name['State']
State = enum_type_wrapper.EnumTypeWrapper(_STATE)
POISON_IVY = 0
DEHYDRATION = 1
HYPOTHERMIA_START = 2
HYPOTHERMIA_END = 3


_GAMESTATE = DESCRIPTOR.message_types_by_name['GameState']
GameState = _reflection.GeneratedProtocolMessageType('GameState', (_message.Message,), {
  'DESCRIPTOR' : _GAMESTATE,
  '__module__' : 'gamestate_pb2'
  # @@protoc_insertion_point(class_scope:GameState)
  })
_sym_db.RegisterMessage(GameState)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'H\003'
  _STATE._serialized_start=55
  _STATE._serialized_end=139
  _GAMESTATE._serialized_start=19
  _GAMESTATE._serialized_end=53
# @@protoc_insertion_point(module_scope)
