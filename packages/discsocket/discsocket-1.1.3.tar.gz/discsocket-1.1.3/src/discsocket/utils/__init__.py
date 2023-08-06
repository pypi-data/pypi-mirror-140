from .cdn import return_cdn_avatar

# Set interaction opcodes
DISPATCH = 0
HEARTBEAT = 1
IDENTIFY = 2
RESUME = 6
RECONNECT = 7
INVALID_SESSION = 9
HELLO = 10
HEARTBEAT_ACK = 11

# Set application command types
SLASH = 2
USER = 2
MESSAGE = 3

# Set message response types
CHANNEL_WITH_SOURCE = 4
DEFERRED_CHANNEL_WITH_SOURCE = 5
DEFERRED_UPDATE_MESSAGE = 6
UPDATE_MESSAGE = 7
AUTOCOMPLETE_RESULT = 8

__version__ = '1.1.3'