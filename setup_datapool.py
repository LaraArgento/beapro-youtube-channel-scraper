from botcity.maestro import (
    BotMaestroSDK,
    DataPool,
    DataPoolEntry,
    SchemaField,
    FieldType,
)

from botcity.maestro.datapool.enums import TriggerEnum


from config import get_env_credentials
login, key, server, _ = get_env_credentials()

DATAPOOL_LABEL = "YoutubeChannels"

BotMaestroSDK.VERIFY_SSL_CERT = False
maestro = BotMaestroSDK.from_sys_args(
    default_server=server,
    default_login=login,
    default_key=key,
)


pool = DataPool(
    label=DATAPOOL_LABEL,
    name="YoutubeChannels",
    default_automation="YoutubeChannels",
    max_auto_retry=2,
    max_errors_before_inactive=5,
    item_max_processing_time=5,
    schema=[
        SchemaField(label="channel_handle", type=FieldType.TEXT, unique_id=False, display_value=True),
    ],
    # Always create a task when an item is added to datapool
    trigger=TriggerEnum.ALWAYS
)
try:
    maestro.create_datapool(pool)
    print("Datapool created.")
except Exception:
    print("Datapool already exists, skipping creation.")

dp = maestro.get_datapool(DATAPOOL_LABEL)

channels = [
    {"channel_handle": "@botcity_br"},
    {"channel_handle": "@Google"},
    {"channel_handle": "@NASA"},
]

for ch in channels:
    dp.create_entry(DataPoolEntry(values=ch))
    print(f"Added: {ch['channel_handle']}")

print("Datapool created and populated successfully.")
